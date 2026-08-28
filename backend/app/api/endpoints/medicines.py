from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
from pathlib import Path

from app.core.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

UPLOAD_DIR = Path("uploads/medicines")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=schemas.MedicineResponse, status_code=status.HTTP_201_CREATED)
def create_medicine(medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    # Đảm bảo luôn có ít nhất một danh mục trong DB để tránh lỗi khóa ngoại
    category = db.query(models.Category).filter(models.Category.id == medicine.category_id).first()
    if not category:
        category = db.query(models.Category).first()
        if not category:
            category = models.Category(id=1, name="Mặc định", description="Danh mục mặc định")
            db.add(category)
            db.commit()
            db.refresh(category)
        medicine.category_id = category.id
    
    db_medicine = models.Medicine(**medicine.model_dump())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@router.post("/{medicine_id}/upload-image")
def upload_medicine_image(medicine_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Không tìm thấy thuốc")
    
    file_extension = Path(file.filename).suffix
    file_name = f"medicine_{medicine_id}{file_extension}"
    file_path = UPLOAD_DIR / file_name
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    image_url = f"/uploads/medicines/{file_name}"
    if hasattr(db_medicine, "image_url"):
        db_medicine.image_url = image_url
        db.commit()
        
    return {"message": "Tải ảnh lên thành công", "image_url": image_url}

@router.get("/", response_model=List[schemas.MedicineResponse])
def read_medicines(skip: int = 0, limit: int = 100, search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Medicine)
    if search:
        query = query.filter(models.Medicine.name.ilike(f"%{search}%"))
    medicines = query.offset(skip).limit(limit).all()
    return medicines

@router.put("/{medicine_id}", response_model=schemas.MedicineResponse)
def update_medicine(medicine_id: int, medicine: schemas.MedicineCreate, db: Session = Depends(get_db)):
    db_medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Không tìm thấy thuốc")
    
    for key, value in medicine.model_dump().items():
        setattr(db_medicine, key, value)
        
    db.commit()
    db.refresh(db_medicine)
    return db_medicine

@router.delete("/{medicine_id}")
def delete_medicine(medicine_id: int, db: Session = Depends(get_db)):
    db_medicine = db.query(models.Medicine).filter(models.Medicine.id == medicine_id).first()
    if not db_medicine:
        raise HTTPException(status_code=404, detail="Không tìm thấy thuốc")
    db.delete(db_medicine)
    db.commit()
    return {"message": "Đã xóa thuốc thành công"}