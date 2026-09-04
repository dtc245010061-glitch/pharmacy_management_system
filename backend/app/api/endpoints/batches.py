from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.core.security import require_roles
from app.models.models import RoleEnum

router = APIRouter()

@router.post("/", response_model=schemas.BatchResponse, status_code=status.HTTP_201_CREATED)
def create_batch(
    batch: schemas.BatchCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist]))
):
    # Kiểm tra xem thuốc (medicine_id) có tồn tại trong hệ thống không
    medicine = db.query(models.Medicine).filter(models.Medicine.id == batch.medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=400, detail="Không thể nhập lô: Thuốc không tồn tại trong hệ thống")
    
    # Lọc an toàn các trường có trong models.Batch
    batch_dict = batch.model_dump()
    valid_fields = {k: v for k, v in batch_dict.items() if hasattr(models.Batch, k)}

    db_batch = models.Batch(**valid_fields)
    db.add(db_batch)

    # Tự động cộng dồn số lượng tồn kho cho loại thuốc tương ứng
    medicine.quantity = (medicine.quantity or 0) + db_batch.quantity

    db.commit()
    db.refresh(db_batch)
    return db_batch

@router.get("/", response_model=List[schemas.BatchResponse])
def read_batches(
    skip: int = 0, 
    limit: int = 100, 
    medicine_id: Optional[int] = None, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist]))
):
    """
    Lấy danh sách các lô hàng. 
    Hỗ trợ query parameter 'medicine_id' để lọc các lô của một loại thuốc cụ thể.
    Dữ liệu được sắp xếp theo hạn sử dụng tăng dần (FEFO).
    """
    query = db.query(models.Batch)
    if medicine_id is not None:
        query = query.filter(models.Batch.medicine_id == medicine_id)
        
    batches = query.order_by(models.Batch.expiry_date.asc()).offset(skip).limit(limit).all()
    return batches

@router.get("/expiring-soon", response_model=List[schemas.BatchResponse])
def get_expiring_soon_batches(
    days: int = 30, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist]))
):
    """
    Lấy danh sách các lô thuốc đã hết hạn hoặc sắp hết hạn trong vòng N ngày tới
    và vẫn còn tồn kho (quantity > 0) để hiển thị cảnh báo.
    """
    target_date = date.today() + timedelta(days=days)
    batches = (
        db.query(models.Batch)
        .filter(models.Batch.expiry_date <= target_date, models.Batch.quantity > 0)
        .order_by(models.Batch.expiry_date.asc())
        .all()
    )
    return batches

@router.get("/{batch_id}", response_model=schemas.BatchResponse)
def read_batch(
    batch_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist]))
):
    batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if batch is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô hàng")
    return batch

@router.delete("/{batch_id}")
def delete_batch(
    batch_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager]))
):
    """
    Xóa lô hàng và tự động trừ số lượng tồn kho tương ứng của thuốc (Chỉ dành riêng cho Quản lý).
    """
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="Không tìm thấy lô hàng")

    # Giảm trừ số lượng tồn kho của thuốc tương ứng
    medicine = db.query(models.Medicine).filter(models.Medicine.id == db_batch.medicine_id).first()
    if medicine:
        medicine.quantity = max(0, (medicine.quantity or 0) - db_batch.quantity)

    db.delete(db_batch)
    db.commit()
    return {"message": "Đã xóa lô thuốc thành công"}