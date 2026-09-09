from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Any, Dict, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.core.security import require_roles
from app.models.models import RoleEnum

router = APIRouter()

class POSCheckoutItem(BaseModel):
    medicine_id: int
    quantity: int = Field(gt=0, description="Số lượng mua phải lớn hơn 0")

class POSCheckoutRequest(BaseModel):
    items: List[POSCheckoutItem]
    user_id: Optional[int] = None

@router.post("/", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_in: POSCheckoutRequest, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist, RoleEnum.cashier]))
):
    """
    Thanh toán đơn hàng và tự động trừ kho theo chuẩn FEFO (First Expired, First Out).
    """
    if not invoice_in.items:
        raise HTTPException(status_code=400, detail="Giỏ hàng không có sản phẩm để thanh toán.")

    total_amount = 0.0
    details_to_create = []

    for item in invoice_in.items:
        # 1. Kiểm tra sự tồn tại của thuốc (chỉ chọn cột có sẵn trong CSDL vật lý)
        med = (
            db.query(models.Medicine.id, models.Medicine.name)
            .filter(models.Medicine.id == item.medicine_id)
            .first()
        )
        if not med:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thuốc ID: {item.medicine_id}")
        
        # 2. Lấy danh sách các lô còn hàng, sắp xếp theo HSD tăng dần (FEFO)
        batches = (
            db.query(
                models.Batch.id,
                models.Batch.batch_number,
                models.Batch.quantity,
                models.Batch.sell_price,
                models.Batch.expiry_date
            )
            .filter(
                models.Batch.medicine_id == item.medicine_id,
                models.Batch.quantity > 0
            )
            .order_by(models.Batch.expiry_date.asc())
            .all()
        )

        total_available = sum(b.quantity for b in batches)
        if total_available < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Thuốc '{med.name}' không đủ tồn kho. Tồn hiện tại: {total_available}, Yêu cầu: {item.quantity}"
            )
        
        # 3. Trừ kho từng lô theo nguyên tắc FEFO
        remaining_to_deduct = item.quantity

        for b in batches:
            if remaining_to_deduct <= 0:
                break
            
            deduct_qty = min(b.quantity, remaining_to_deduct)
            new_batch_qty = b.quantity - deduct_qty
            remaining_to_deduct -= deduct_qty

            # Cập nhật số lượng tồn của lô vào CSDL
            db.query(models.Batch).filter(models.Batch.id == b.id).update(
                {models.Batch.quantity: new_batch_qty}
            )

            line_price = b.sell_price or 0.0
            total_amount += deduct_qty * line_price

            details_to_create.append({
                "batch_id": b.id,
                "quantity": deduct_qty,
                "price": line_price
            })

    # 4. Lưu hóa đơn vào cơ sở dữ liệu
    db_invoice = models.Invoice(
        user_id=current_user.id,
        total_amount=round(total_amount, 2),
        created_at=datetime.utcnow()
    )
    db.add(db_invoice)
    db.flush()

    # 5. Lưu chi tiết hóa đơn theo từng lô xuất kho
    for d in details_to_create:
        db_detail = models.InvoiceDetail(
            invoice_id=db_invoice.id,
            batch_id=d["batch_id"],
            quantity=d["quantity"],
            price=d["price"]
        )
        db.add(db_detail)
    
    db.commit()
    db.refresh(db_invoice)
    return db_invoice

@router.get("/", response_model=List[schemas.InvoiceResponse])
def get_invoices(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist, RoleEnum.cashier]))
):
    """Lấy danh sách hóa đơn, sắp xếp theo thời gian mới nhất lên đầu"""
    invoices = (
        db.query(models.Invoice)
        .order_by(models.Invoice.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return invoices

@router.get("/{invoice_id}")
def get_invoice_detail(
    invoice_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist, RoleEnum.cashier]))
) -> Dict[str, Any]:
    """Lấy chi tiết từng dòng thuốc trong hóa đơn kèm thông tin lô và đơn vị tính"""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")

    items = (
        db.query(
            models.InvoiceDetail.id,
            models.InvoiceDetail.quantity,
            models.InvoiceDetail.price,
            models.Medicine.id.label("medicine_id"),
            models.Medicine.name.label("medicine_name"),
            models.Medicine.unit.label("unit"),
            models.Batch.batch_number.label("batch_number")
        )
        .join(models.Batch, models.InvoiceDetail.batch_id == models.Batch.id)
        .join(models.Medicine, models.Batch.medicine_id == models.Medicine.id)
        .filter(models.InvoiceDetail.invoice_id == invoice_id)
        .all()
    )

    detail_items = []
    for item in items:
        detail_items.append({
            "id": item.id,
            "medicine_id": item.medicine_id,
            "medicine_name": item.medicine_name,
            "unit": item.unit,
            "batch_number": item.batch_number,
            "quantity": item.quantity,
            "unit_price": item.price,
            "subtotal": round(item.quantity * item.price, 2)
        })

    return {
        "id": invoice.id,
        "total_amount": invoice.total_amount,
        "created_at": invoice.created_at.strftime("%Y-%m-%d %H:%M:%S") if invoice.created_at else None,
        "items": detail_items
    }