from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1. Xác định đường dẫn tuyệt đối đến thư mục 'backend'
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BACKEND_DIR / "pharmacy.db"

# 2. Chuẩn hóa DATABASE_URL: Nếu đang dùng đường dẫn tương đối thì ép về file cố định trong backend
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite:///./") or database_url == "sqlite:///pharmacy.db":
    database_url = f"sqlite:///{DB_FILE.as_posix()}"

# Sử dụng check_same_thread=False vì FastAPI xử lý bất đồng bộ, SQLite cần cấu hình này
engine = create_engine(
    database_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()