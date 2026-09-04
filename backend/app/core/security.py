from datetime import datetime, timedelta
from typing import Optional, List, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import models
from app.models.models import RoleEnum

# Cấu hình thuật toán băm mật khẩu
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Khai báo scheme lấy token từ Authorization Header (Bearer token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """
    Giải mã JWT token, kiểm tra tính hợp lệ và trả về đối tượng User hiện tại.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Phiên đăng nhập không hợp lệ hoặc đã hết hạn",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản này hiện đang bị khóa"
        )
    return user

def require_roles(allowed_roles: List[Union[RoleEnum, str]]):
    """
    Dependency kiểm tra quyền truy cập theo vai trò:
    Ví dụ: Depends(require_roles([RoleEnum.manager, RoleEnum.pharmacist]))
    """
    def role_checker(current_user: models.User = Depends(get_current_user)) -> models.User:
        user_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
        allowed = [r.value if hasattr(r, "value") else str(r) for r in allowed_roles]
        
        if user_role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Truy cập bị từ chối. Thao tác chỉ dành cho: {', '.join(allowed)}"
            )
        return current_user
    return role_checker