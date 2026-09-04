# BẢN ĐỒ API & PHÂN QUYỀN (API MAP & RBAC)

> Tự động sinh bởi script `scripts/generate_api_map.py`.
> Thời gian cập nhật: `2026-09-04 10:27:26`

## 📊 Thống kê tổng quan
- **Tổng số API Endpoints:** `27`
- **Endpoints được bảo vệ bởi RBAC / Auth:** `12`
- **Endpoints công khai (Public):** `15`

---

### 📌 Phân hệ: Authentication
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/login` | Login | Công khai (Public) |
| `POST` | `/api/v1/auth/setup-roles` | API tiện ích tạo sẵn 3 tài khoản mẫu tương ứng với 3 vai trò để test phân quyền: | Công khai (Public) |
| `POST` | `/api/v1/auth/setup-admin` | Giữ nguyên endpoint cũ để đảm bảo tương thích ngược | Công khai (Public) |

### 📌 Phân hệ: Categories
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/categories/` | Create category | Công khai (Public) |
| `GET` | `/api/v1/categories/` | Read categories | Công khai (Public) |
| `PUT` | `/api/v1/categories/{category_id}` | Update category | Công khai (Public) |
| `DELETE` | `/api/v1/categories/{category_id}` | Delete category | Công khai (Public) |

### 📌 Phân hệ: Suppliers
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/suppliers/` | Create supplier | `manager` |
| `GET` | `/api/v1/suppliers/` | Read suppliers | `manager`, `pharmacist` |
| `PUT` | `/api/v1/suppliers/{supplier_id}` | Update supplier | `manager` |
| `DELETE` | `/api/v1/suppliers/{supplier_id}` | Delete supplier | `manager` |

### 📌 Phân hệ: Medicines
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/medicines/` | Create medicine | Công khai (Public) |
| `POST` | `/api/v1/medicines/{medicine_id}/upload-image` | Upload medicine image | Công khai (Public) |
| `GET` | `/api/v1/medicines/` | Read medicines | Công khai (Public) |
| `PUT` | `/api/v1/medicines/{medicine_id}` | Update medicine | Công khai (Public) |
| `DELETE` | `/api/v1/medicines/{medicine_id}` | Delete medicine | Công khai (Public) |

### 📌 Phân hệ: AI Integration
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/ai/consult` | Trợ lý AI Dược học kết hợp dữ liệu kho thuốc nội bộ theo thời gian thực (RAG thu nhỏ). | Công khai (Public) |
| `POST` | `/api/v1/ai/check-interactions` | Phân tích tương tác chéo giữa các loại thuốc trong giỏ hàng trước khi xuất đơn. | Công khai (Public) |

### 📌 Phân hệ: Invoices / POS
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/invoices/` | Create invoice | `manager`, `pharmacist`, `cashier` |
| `GET` | `/api/v1/invoices/` | Lấy danh sách hóa đơn, sắp xếp theo thời gian mới nhất lên đầu | `manager`, `pharmacist`, `cashier` |
| `GET` | `/api/v1/invoices/{invoice_id}` | Lấy chi tiết từng dòng thuốc trong hóa đơn kèm tên thuốc và đơn vị tính | `manager`, `pharmacist`, `cashier` |

### 📌 Phân hệ: Inventory Batches
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/batches/` | Create batch | `manager`, `pharmacist` |
| `GET` | `/api/v1/batches/` | Lấy danh sách các lô hàng.  | `manager`, `pharmacist` |
| `GET` | `/api/v1/batches/expiring-soon` | Lấy danh sách các lô thuốc đã hết hạn hoặc sắp hết hạn trong vòng N ngày tới | `manager`, `pharmacist` |
| `GET` | `/api/v1/batches/{batch_id}` | Read batch | `manager`, `pharmacist` |
| `DELETE` | `/api/v1/batches/{batch_id}` | Xóa lô hàng và tự động trừ số lượng tồn kho tương ứng của thuốc (Chỉ dành riêng cho Quản lý). | `manager` |

### 📌 Phân hệ: General
| Phương thức | Đường dẫn API | Chức năng / Mô tả | Phân quyền truy cập |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Root | Công khai (Public) |

---
*Tài liệu tự động đồng bộ từ cấu hình router thực tế của Backend.*