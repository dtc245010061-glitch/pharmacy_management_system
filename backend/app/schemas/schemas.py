from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.models import RoleEnum

# ==========================
# 1. User Schemas
# ==========================
class UserBase(BaseModel):
    username: str
    role: RoleEnum
    is_active: Optional[int] = 1

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 2. Category Schemas
# ==========================
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 3. Medicine Schemas
# ==========================
class MedicineBase(BaseModel):
    name: str
    category_id: int
    unit: str
    description: Optional[str] = None
    is_approved: Optional[int] = 0

class MedicineCreate(MedicineBase):
    pass

class MedicineResponse(MedicineBase):
    id: int
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)

class MedicineBase(BaseModel):
    name: str
    unit: str
    category_id: int
    description: Optional[str] = None
    quantity: int = 0  # <--- Bổ sung dòng này

# ==========================
# 4. Batch Schemas
# ==========================
class BatchBase(BaseModel):
    medicine_id: int
    batch_number: str
    expiry_date: date
    quantity: int = Field(ge=0, description="Số lượng không được âm")
    import_price: float = Field(ge=0)
    sell_price: float = Field(ge=0)
    supplier: Optional[str] = None

class BatchCreate(BatchBase):
    pass

class BatchResponse(BatchBase):
    id: int
    import_date: datetime
    medicine: Optional[MedicineResponse] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 5. Invoice Schemas (Hóa đơn & Chi tiết)
# ==========================
class InvoiceDetailBase(BaseModel):
    batch_id: int
    quantity: int = Field(gt=0, description="Số lượng bán phải lớn hơn 0")

class InvoiceDetailCreate(InvoiceDetailBase):
    pass

class InvoiceDetailResponse(InvoiceDetailBase):
    id: int
    invoice_id: int
    price: float

    model_config = ConfigDict(from_attributes=True)

class InvoiceBase(BaseModel):
    user_id: int

class InvoiceCreate(InvoiceBase):
    # Khi tạo hóa đơn, Frontend sẽ gửi lên danh sách các mặt hàng (batch) cần bán
    details: List[InvoiceDetailCreate]

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime
    total_amount: float
    details: List[InvoiceDetailResponse] = []

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 6. AI & Báo cáo Schemas
# ==========================
class AIQueryRequest(BaseModel):
    query: str
    context_type: str = Field(..., description="Loại context: 'medicine_info', 'sop', 'expiry_report'")
    medicine_id: Optional[int] = None

class AIQueryResponse(BaseModel):
    result: str
    warning: str = "LƯU Ý: Đây là thông tin tham khảo từ AI. Không thay thế lời khuyên y tế của Dược sĩ/Bác sĩ."
    # ==========================
# 7. Cart & Checkout Schemas (MỚI)
# ==========================
class CartItem(BaseModel):
    medicine_id: int
    quantity: int = Field(gt=0, description="Số lượng mua phải lớn hơn 0")

class CheckoutRequest(BaseModel):
    user_id: int # ID của thu ngân (Sau này sẽ lấy tự động từ JWT Token)
    items: List[CartItem]
# ==========================
# 8. Auth & Login Schemas (MỚI)
# ==========================
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str