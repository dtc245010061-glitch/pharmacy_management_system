from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class RoleEnum(str, enum.Enum):
    manager = "manager"
    pharmacist = "pharmacist"
    cashier = "cashier"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    is_active = Column(Integer, default=1)

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    
    medicines = relationship("Medicine", back_populates="category")

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)

    batches = relationship("Batch", back_populates="supplier_ref")

class Medicine(Base):
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))
    unit = Column(String(50), nullable=False) # Hộp, Vỉ, Viên...
    description = Column(Text) # Thông tin thuốc chuẩn để đưa cho AI
    is_approved = Column(Integer, default=0) # 1: Đã được dược sĩ duyệt để AI dùng
    quantity = Column(Integer, default=0) # Tổng tồn kho tích lũy
    image_url = Column(String(255), nullable=True) # Đường dẫn ảnh thuốc
    
    category = relationship("Category", back_populates="medicines")
    batches = relationship("Batch", back_populates="medicine")

class Batch(Base):
    __tablename__ = "batches"
    
    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(Integer, ForeignKey("medicines.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True) # Khóa ngoại sang bảng Supplier
    batch_number = Column(String(100), index=True, nullable=False)
    import_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False) # Số lượng tồn kho hiện tại của lô
    import_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)
    supplier = Column(String(255), nullable=True) # Giữ nguyên trường text cũ để tương thích
    
    medicine = relationship("Medicine", back_populates="batches")
    supplier_ref = relationship("Supplier", back_populates="batches")
    invoice_details = relationship("InvoiceDetail", back_populates="batch")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Thu ngân tạo hóa đơn
    created_at = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0.0)
    
    details = relationship("InvoiceDetail", back_populates="invoice")

class InvoiceDetail(Base):
    __tablename__ = "invoice_details"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    batch_id = Column(Integer, ForeignKey("batches.id"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False) # Lưu cứng giá bán tại thời điểm lập hóa đơn
    
    invoice = relationship("Invoice", back_populates="details")
    batch = relationship("Batch", back_populates="invoice_details")