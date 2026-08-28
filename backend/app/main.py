from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from pathlib import Path

app = FastAPI(title="AI-powered Pharmacy Management System")

# Cấu hình CORS để Frontend có thể giao tiếp được với Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả các domain gọi API (khi test)
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép mọi phương thức (GET, POST, PUT, DELETE, OPTIONS...)
    allow_headers=["*"],
)

# Đăng ký thư mục tĩnh để hiển thị ảnh upload
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Pharmacy Management System API is running"}