from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import models
from app.schemas import schemas
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.models import RoleEnum

router = APIRouter()

@router.post("/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Tìm user trong DB (Đã sửa lỗi request.request.username thành request.username)
    user = db.query(models.User).filter(models.User.username == request.username).first()
    
    # Kiểm tra tồn tại và khớp mật khẩu
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu"
        )
    
    # Tạo JWT Token chứa thông tin role
    access_token = create_access_token(data={"sub": user.username, "role": user.role.value})
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role.value}

@router.post("/setup-admin")
def setup_default_admin(db: Session = Depends(get_db)):
    """API tiện ích để tạo tài khoản Admin ban đầu test hệ thống"""
    user = db.query(models.User).filter(models.User.username == "admin").first()
    if user:
        return {"message": "Tài khoản admin đã tồn tại. Pass: 123456"}
    
    admin_user = models.User(
        username="admin",
        hashed_password=get_password_hash("123456"),
        role=RoleEnum.manager,
        is_active=1
    )
    db.add(admin_user)
    db.commit()
    return {"message": "Đã tạo tài khoản thành công. User: admin | Pass: 123456"}