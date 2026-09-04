# TỪ ĐIỂN DỮ LIỆU & SƠ ĐỒ CSDL (DATABASE SCHEMA)

> Tự động sinh bởi script `scripts/generate_db_schema.py`.
> Thời gian cập nhật: `2026-09-04 10:43:45`

## 📊 Thống kê tổng quan
- **Tổng số bảng (Tables):** `7`
- **Tổng số trường dữ liệu (Columns):** `40`

---

### 🗄️ Bảng: `batches`
| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INT` | **PK** | Không | - | - |
| `medicine_id` | `INT` |  | Có | `medicines.id` | - |
| `supplier_id` | `INT` |  | Có | `suppliers.id` | - |
| `batch_number` | `VARCHAR(100)` |  | Không | - | - |
| `import_date` | `DATETIME` |  | Có | - | `<function datetime.utcnow at 0x0000020E7C1EE5C0>` |
| `expiry_date` | `DATE` |  | Không | - | - |
| `quantity` | `INT` |  | Không | - | - |
| `import_price` | `FLOAT` |  | Không | - | - |
| `sell_price` | `FLOAT` |  | Không | - | - |
| `supplier` | `VARCHAR(255)` |  | Có | - | - |

### 🗄️ Bảng: `categories`
| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INT` | **PK** | Không | - | - |
| `name` | `VARCHAR(100)` |  | Không | - | - |
| `description` | `VARCHAR(255)` |  | Có | - | - |

### 🗄️ Bảng: `invoice_details`
| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INT` | **PK** | Không | - | - |
| `invoice_id` | `INT` |  | Có | `invoices.id` | - |
| `batch_id` | `INT` |  | Có | `batches.id` | - |
| `quantity` | `INT` |  | Không | - | - |
| `price` | `FLOAT` |  | Không | - | - |

### 🗄️ Bảng: `invoices`
| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INT` | **PK** | Không | - | - |
| `user_id` | `INT` |  | Có | `users.id` | - |
| `created_at` | `DATETIME` |  | Có | - | `<function datetime.utcnow at 0x0000020E7C1EF880>` |
| `total_amount` | `FLOAT` |  | Có | - | `0.0` |

### 🗄️ Bảng: `medicines`
| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INT` | **PK** | Không | - | - |
| `name` | `VARCHAR(255)` |  | Không | - | - |
| `category_id` | `INT` |  | Có | `categories.id` | - |
| `unit` | `VARCHAR(50)` |  | Không | - | - |
| `description` | `TEXT` |  | Có | - | - |
| `is_approved` | `INT` |  | Có | - | `0` |
| `quantity` | `INT` |  | Có | - | `0` |
| `image_url` | `VARCHAR(255)` |  | Có | - | - |

### 🗄️ Bảng: `suppliers`
| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INT` | **PK** | Không | - | - |
| `name` | `VARCHAR(255)` |  | Không | - | - |
| `phone` | `VARCHAR(50)` |  | Có | - | - |
| `email` | `VARCHAR(100)` |  | Có | - | - |
| `address` | `VARCHAR(255)` |  | Có | - | - |

### 🗄️ Bảng: `users`
| Tên cột | Kiểu dữ liệu | Khóa | Bắt buộc | Khóa ngoại / Tham chiếu | Mặc định |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `id` | `INT` | **PK** | Không | - | - |
| `username` | `VARCHAR(50)` |  | Không | - | - |
| `hashed_password` | `VARCHAR(255)` |  | Không | - | - |
| `role` | `VARCHAR(10)` |  | Không | - | - |
| `is_active` | `INT` |  | Có | - | `1` |

---
*Tài liệu tự động đồng bộ trực tiếp từ SQLAlchemy ORM Models của Backend.*