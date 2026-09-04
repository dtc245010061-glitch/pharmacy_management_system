from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.core.security import require_roles
from app.models.models import RoleEnum

router = APIRouter()

@router.post("/", response_model=schemas.SupplierResponse, status_code=status.HTTP_201_CREATED)
def create_supplier(
    supplier: schemas.SupplierCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager]))
):
    # Kiểm tra trùng tên nhà cung cấp
    existing = db.query(models.Supplier).filter(models.Supplier.name == supplier.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tên nhà cung cấp này đã tồn tại")

    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.get("/", response_model=List[schemas.SupplierResponse])
def read_suppliers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist]))
):
    return db.query(models.Supplier).offset(skip).limit(limit).all()

@router.put("/{supplier_id}", response_model=schemas.SupplierResponse)
def update_supplier(
    supplier_id: int, 
    supplier_in: schemas.SupplierCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager]))
):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")
    
    for key, value in supplier_in.model_dump().items():
        setattr(db_supplier, key, value)
        
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles([RoleEnum.manager]))
):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà cung cấp")
    
    db.delete(db_supplier)
    db.commit()
    return {"message": "Đã xóa nhà cung cấp thành công"}