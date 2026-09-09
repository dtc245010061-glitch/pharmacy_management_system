import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "pharmacy.db")

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"[-] Không tìm thấy file database tại {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Kiểm tra các cột hiện có trong bảng medicines
    cursor.execute("PRAGMA table_info(medicines);")
    existing_med_cols = [col[1] for col in cursor.fetchall()]

    new_med_columns = [
        ("quantity", "INTEGER DEFAULT 0"),
        ("registration_number", "VARCHAR(100)"),
        ("ingredients", "TEXT"),
        ("dosage_form", "VARCHAR(100)"),
        ("packaging", "VARCHAR(255)"),
        ("manufacturer", "VARCHAR(255)"),
        ("country", "VARCHAR(100)"),
        ("image_url", "VARCHAR(255)")
    ]

    for col_name, col_type in new_med_columns:
        if col_name not in existing_med_cols:
            cursor.execute(f"ALTER TABLE medicines ADD COLUMN {col_name} {col_type};")
            print(f"[+] Bảng medicines: Đã thêm cột '{col_name}' ({col_type})")
        else:
            print(f"[*] Bảng medicines: Cột '{col_name}' đã tồn tại.")

    # 2. Kiểm tra các cột hiện có trong bảng batches
    cursor.execute("PRAGMA table_info(batches);")
    existing_batch_cols = [col[1] for col in cursor.fetchall()]

    new_batch_columns = [
        ("supplier_id", "INTEGER")
    ]

    for col_name, col_type in new_batch_columns:
        if col_name not in existing_batch_cols:
            cursor.execute(f"ALTER TABLE batches ADD COLUMN {col_name} {col_type};")
            print(f"[+] Bảng batches: Đã thêm cột '{col_name}' ({col_type})")
        else:
            print(f"[*] Bảng batches: Cột '{col_name}' đã tồn tại.")

    conn.commit()
    conn.close()
    print("\n>>> Hoàn tất cập nhật CSDL SQLite an toàn! <<<")

if __name__ == "__main__":
    migrate()