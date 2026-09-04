from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any, Dict
from datetime import datetime

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.core.security import require_roles
from app.models.models import RoleEnum

router = APIRouter()

@router.post("/", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice_in: schemas.InvoiceCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist, RoleEnum.cashier]))
):
    total_amount = 0.0
    invoice_items_data = []

    for item in invoice_in.items:
        medicine = db.query(models.Medicine).filter(models.Medicine.id == item.medicine_id).first()
        if not medicine:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thuốc ID: {item.medicine_id}")
        
        # Lấy danh sách các lô còn hàng, sắp xếp theo hạn sử dụng tăng dần (FEFO)
        batches = db.query(models.Batch).filter(
            models.Batch.medicine_id == item.medicine_id,
            models.Batch.quantity > 0
        ).order_by(models.Batch.expiry_date.asc()).all()

        total_available = sum(b.quantity for b in batches)
        if total_available < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Thuốc '{medicine.name}' không đủ tồn kho. Tồn hiện tại: {total_available}, Yêu cầu: {item.quantity}"
            )
        
        # Tiến hành trừ kho theo nguyên tắc FEFO
        remaining_to_deduct = item.quantity
        item_total_price = 0.0

        for batch in batches:
            if remaining_to_deduct <= 0:
                break
            
            if batch.quantity >= remaining_to_deduct:
                batch.quantity -= remaining_to_deduct
                item_total_price += remaining_to_deduct * batch.sale_price
                remaining_to_deduct = 0
            else:
                deduct = batch.quantity
                remaining_to_deduct -= deduct
                item_total_price += deduct * batch.sale_price
                batch.quantity = 0
            
            db.add(batch)

        # Cập nhật đồng bộ tổng số lượng tồn kho của loại thuốc
        medicine.quantity = max(0, (medicine.quantity or 0) - item.quantity)
        db.add(medicine)

        total_amount += item_total_price
        invoice_items_data.append({
            "medicine_id": item.medicine_id,
            "quantity": item.quantity,
            "unit_price": item_total_price / item.quantity if item.quantity > 0 else 0
        })

    # Lưu hóa đơn vào cơ sở dữ liệu
    db_invoice = models.Invoice(
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    # Lưu chi tiết hóa đơn
    for itm in invoice_items_data:
        db_item = models.InvoiceItem(
            invoice_id=db_invoice.id,
            medicine_id=itm["medicine_id"],
            quantity=itm["quantity"],
            unit_price=itm["unit_price"]
        )
        db.add(db_item)
    
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
    """Lấy chi tiết từng dòng thuốc trong hóa đơn kèm tên thuốc và đơn vị tính"""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Không tìm thấy hóa đơn")

    items = (
        db.query(models.InvoiceItem, models.Medicine.name, models.Medicine.unit)
        .join(models.Medicine, models.InvoiceItem.medicine_id == models.Medicine.id)
        .filter(models.InvoiceItem.invoice_id == invoice_id)
        .all()
    )

    detail_items = []
    for item, med_name, med_unit in items:
        detail_items.append({
            "id": item.id,
            "medicine_id": item.medicine_id,
            "medicine_name": med_name,
            "unit": med_unit,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "subtotal": round(item.quantity * item.unit_price, 2)
        })

    return {
        "id": invoice.id,
        "total_amount": invoice.total_amount,
        "created_at": invoice.created_at.strftime("%Y-%m-%d %H:%M:%S") if invoice.created_at else None,
        "items": detail_items
    }