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
    # Tìm user trong DB
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

@router.post("/setup-roles")
def setup_default_roles(db: Session = Depends(get_db)):
    """
    API tiện ích tạo sẵn 3 tài khoản mẫu tương ứng với 3 vai trò để test phân quyền:
    - manager:    user 'admin'    | pass '123456'
    - pharmacist: user 'duocsi'   | pass '123456'
    - cashier:    user 'thungan'  | pass '123456'
    """
    accounts = [
        {"username": "admin", "role": RoleEnum.manager, "pass": "123456"},
        {"username": "duocsi", "role": RoleEnum.pharmacist, "pass": "123456"},
        {"username": "thungan", "role": RoleEnum.cashier, "pass": "123456"},
    ]
    created = []
    for acc in accounts:
        existing = db.query(models.User).filter(models.User.username == acc["username"]).first()
        if not existing:
            new_user = models.User(
                username=acc["username"],
                hashed_password=get_password_hash(acc["pass"]),
                role=acc["role"],
                is_active=1
            )
            db.add(new_user)
            created.append(acc["username"])
    
    db.commit()
    return {
        "message": "Khởi tạo thành công danh sách tài khoản kiểm thử",
        "created_accounts": created,
        "test_accounts": [
            {"role": "manager (Quản lý)", "username": "admin", "password": "123456"},
            {"role": "pharmacist (Dược sĩ)", "username": "duocsi", "password": "123456"},
            {"role": "cashier (Thu ngân)", "username": "thungan", "password": "123456"}
        ]
    }

@router.post("/setup-admin")
def setup_default_admin(db: Session = Depends(get_db)):
    """Giữ nguyên endpoint cũ để đảm bảo tương thích ngược"""
    return setup_default_roles(db)