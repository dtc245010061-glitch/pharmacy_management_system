from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

@router.post("/", response_model=schemas.BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(batch: schemas.BatchCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem thuốc (medicine_id) có tồn tại trong hệ thống không
    medicine = db.query(models.Medicine).filter(models.Medicine.id == batch.medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=400, detail="Không thể nhập lô: Thuốc không tồn tại trong hệ thống")
    
    # Tạo lô hàng mới
    db_batch = models.Batch(**batch.model_dump())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.get("/", response_model=List[schemas.BatchResponse])
def read_batches(skip: int = 0, limit: int = 100, medicine_id: int = None, db: Session = Depends(get_db)):
    """
    Lấy danh sách các lô hàng. 
    Hỗ trợ query parameter 'medicine_id' để lọc các lô của một loại thuốc cụ thể.
    """
    query = db.query(models.Batch)
    if medicine_id is not None:
        query = query.filter(models.Batch.medicine_id == medicine_id)
        
    batches = query.offset(skip).limit(limit).all()
    return batches

@router.get("/{batch_id}", response_model=schemas.BatchResponse)
def read_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô hàng")
    return batch