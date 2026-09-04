import os
import sys
from pathlib import Path
from datetime import datetime

# 1. Định vị thư mục gốc và thư mục backend
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"

# Thêm backend vào sys.path để import module app lúc runtime
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Tải biến môi trường từ backend/.env hoặc .env ở thư mục gốc
try:
    from dotenv import load_dotenv
    if (backend_dir / ".env").exists():
        load_dotenv(backend_dir / ".env")
    elif (root_dir / ".env").exists():
        load_dotenv(root_dir / ".env")
except ImportError:
    pass

# Đặt biến môi trường dự phòng để Pydantic Settings không bị thiếu khi chỉ đọc metadata
os.environ.setdefault("PROJECT_NAME", "Pharmacy AI System")
os.environ.setdefault("DATABASE_URL", "sqlite:///./pharmacy.db")
os.environ.setdefault("SECRET_KEY", "temporary-secret-key-for-schema-generator")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
os.environ.setdefault("GEMINI_API_KEY", "temporary-gemini-key")

# 2. Nạp models và Base từ backend
try:
    from app.models import models  # type: ignore
    Base = getattr(models, "Base", None)
    if Base is None:
        from app.core.database import Base  # type: ignore
except Exception as e:
    print(f"[LỖI] Không thể nạp models từ app.models: {e}")
    sys.exit(1)

def format_column_type(col_type) -> str:
    """Định dạng kiểu dữ liệu hiển thị ngắn gọn, dễ đọc."""
    type_str = str(col_type)
    return type_str.replace("VARCHAR", "VARCHAR").replace("INTEGER", "INT")

def generate_db_schema():
    output_file = root_dir / "DB-SCHEMA.md"
    tables = Base.metadata.tables

    if not tables:
        print("[CẢNH BÁO] Không tìm thấy bảng nào trong Base.metadata.")
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_tables = len(tables)
    total_columns = sum(len(tbl.columns) for tbl in tables.values())

    lines = [
        "# TỪ ĐIỂN DỮ LIỆU & SƠ ĐỒ CSDL (DATABASE SCHEMA)\n",
        f"> Tự động sinh bởi script `scripts/generate_db_schema.py`.",
        f"> Thời gian cập nhật: `{now_str}`\n",
        "## 📊 Thống kê tổng quan",
        f"- **Tổng số bảng (Tables):** `{total_tables}`",
        f"- **Tổng số trường dữ liệu (Columns):** `{total_columns}`\n",
        "---"
    ]

    for table_name, table in sorted(tables.items()):
        lines.append(f"\n### 🗄️ Bảng: `{table_name}`")
        lines.append("| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |")
        lines.append("| :--- | :--- | :---: | :---: | :--- | :--- |")

        for col in table.columns:
            key_type = "**PK**" if col.primary_key else ""
            nullable_str = "Không" if not col.nullable else "Có"

            fk_list = []
            for fk in col.foreign_keys:
                fk_list.append(f"`{fk.target_fullname}`")
            fk_str = ", ".join(fk_list) if fk_list else "-"

            default_val = "-"
            if col.default is not None:
                default_val = f"`{col.default.arg}`" if hasattr(col.default, "arg") else "`Defined`"
            elif col.server_default is not None:
                default_val = f"`{col.server_default.arg}`" if hasattr(col.server_default, "arg") else "`Server`"

            lines.append(
                f"| `{col.name}` | `{format_column_type(col.type)}` | {key_type} | {nullable_str} | {fk_str} | {default_val} |"
            )

    lines.append("\n---\n*Tài liệu tự động đồng bộ trực tiếp từ SQLAlchemy ORM Models của Backend.*")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[OK] Đã quét thành công {total_tables} bảng với {total_columns} cột.")
    print(f"[OK] Đã xuất sơ đồ CSDL vào file: {output_file.name}")

if __name__ == "__main__":
    generate_db_schema()