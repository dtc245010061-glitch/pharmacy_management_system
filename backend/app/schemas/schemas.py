from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.models import RoleEnum

# ==========================
# 1. User & Auth Schemas
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

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

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
# 3. Supplier Schemas (MỚI)
# ==========================
class SupplierBase(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierResponse(SupplierBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 4. Medicine Schemas (Đã hợp nhất)
# ==========================
class MedicineBase(BaseModel):
    name: str
    category_id: int
    unit: str
    description: Optional[str] = None
    quantity: int = 0
    image_url: Optional[str] = None
    is_approved: Optional[int] = 0

class MedicineCreate(MedicineBase):
    pass

class MedicineResponse(MedicineBase):
    id: int
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 5. Batch Schemas (Lô thuốc & Hạn dùng)
# ==========================
class BatchBase(BaseModel):
    medicine_id: int
    batch_number: str
    expiry_date: date
    quantity: int = Field(default=0, ge=0, description="Số lượng không được âm")
    import_price: float = Field(default=0.0, ge=0)
    sell_price: float = Field(default=0.0, ge=0)
    supplier: Optional[str] = None
    supplier_id: Optional[int] = None
    manufacturing_date: Optional[date] = None

class BatchCreate(BatchBase):
    pass

class BatchResponse(BatchBase):
    id: int
    import_date: Optional[datetime] = None
    current_quantity: Optional[int] = None
    initial_quantity: Optional[int] = None
    medicine: Optional[MedicineResponse] = None

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 6. Invoice Schemas (Hóa đơn & Bán hàng)
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
    details: List[InvoiceDetailCreate]

class InvoiceResponse(InvoiceBase):
    id: int
    created_at: datetime
    total_amount: float
    details: List[InvoiceDetailResponse] = []

    model_config = ConfigDict(from_attributes=True)

# ==========================
# 7. Cart & Checkout Schemas
# ==========================
class CartItem(BaseModel):
    medicine_id: int
    quantity: int = Field(gt=0, description="Số lượng mua phải lớn hơn 0")

class CheckoutRequest(BaseModel):
    user_id: int
    items: List[CartItem]

# ==========================
# 8. AI & Báo cáo Schemas
# ==========================
class AIQueryRequest(BaseModel):
    query: Optional[str] = None
    prompt: Optional[str] = None
    context_type: Optional[str] = Field(default="medicine_info", description="Loại context: 'medicine_info', 'sop', 'expiry_report'")
    medicine_id: Optional[int] = None

class AIQueryResponse(BaseModel):
    result: str
    warning: str = "LƯU Ý: Đây là thông tin tham khảo từ AI. Không thay thế lời khuyên y tế của Dược sĩ/Bác sĩ."