from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

@router.post("/", response_model=schemas.InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(invoice_in: schemas.InvoiceCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra tổng tiền và tạo hóa đơn khung
    total_amount = 0.0
    invoice_items_data = []

    for item in invoice_in.items:
        medicine = db.query(models.Medicine).filter(models.Medicine.id == item.medicine_id).first()
        if not medicine:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thuốc ID: {item.medicine_id}")
        
        # Lấy danh sách các lô còn hàng, sắp xếp theo hạn sử dụng tăng dần (FEFO: cận date lên đầu)
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
                # Lô này đủ đáp ứng phần còn thiếu
                batch.quantity -= remaining_to_deduct
                item_total_price += remaining_to_deduct * batch.sale_price
                remaining_to_deduct = 0
            else:
                # Lô này không đủ, lấy hết và tiếp tục trừ lô tiếp theo
                deduct = batch.quantity
                remaining_to_deduct -= deduct
                item_total_price += deduct * batch.sale_price
                batch.quantity = 0
            
            db.add(batch)

        total_amount += item_total_price
        invoice_items_data.append({
            "medicine_id": item.medicine_id,
            "quantity": item.quantity,
            "unit_price": item_total_price / item.quantity
        })

    # 2. Lưu hóa đơn vào cơ sở dữ liệu
    db_invoice = models.Invoice(
        total_amount=total_amount,
        created_at=datetime.utcnow()
    )
    db.add(db_invoice)
    db.commit()
    db.refresh(db_invoice)

    # 3. Lưu chi tiết hóa đơn
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
def get_invoices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).offset(skip).limit(limit).all()
    return invoices