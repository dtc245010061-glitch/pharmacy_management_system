# 🏥 Pharmacy AI System - Hệ Thống Quản Lý Nhà Thuốc Tích Hợp AI

Hệ thống Quản lý Nhà thuốc chuẩn GPP được tích hợp Trợ lý AI Dược học (Google Gemini 2.5 Flash), tự động hóa cơ chế xuất kho theo hạn sử dụng **FEFO (First Expired, First Out)** và thiết lập hệ thống kiểm duyệt an toàn (Guardrails) nghiêm ngặt trong tư vấn y tế.

---

## 🚀 Công Nghệ Sử Dụng

- **Backend:** 
  - [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+) - RESTful API hiệu năng cao.
  - [SQLAlchemy](https://www.sqlalchemy.org/) - ORM quản lý dữ liệu.
  - [SQLite](https://www.sqlite.org/) - Cơ sở dữ liệu quan hệ cục bộ, dễ triển khai.
  - [google-genai](https://pypi.org/project/google-genai/) SDK - Tích hợp mô hình `gemini-2.5-flash` có Guardrail.
  - [python-multipart](https://andrew-d.github.io/python-multipart/) - Xử lý tải file ảnh thuốc.
- **Frontend:**
  - [Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/) - Single Page Application hiện đại, tải nhanh.
  - [Vue Router 4](https://router.vuejs.org/) - Định tuyến màn hình và Navigation Guards.
  - [Axios](https://axios-http.com/) - Tương tác API với Interceptor gắn JWT Bearer Token.

---

## 📋 Tính Năng Cốt Lõi

1. **Bảo mật & Phân quyền:** Đăng nhập, cấp phát JWT Token và mã hóa mật khẩu một chiều với Bcrypt.
2. **Quản lý Danh mục & Kho thuốc:** Thêm, xem, sửa, xóa thông tin thuốc, số lượng tồn kho và tải ảnh minh họa sản phẩm.
3. **Quầy Bán Hàng (POS) chuẩn FEFO:** Tự động phát hiện và trừ tồn kho từ các lô thuốc có hạn sử dụng gần nhất trước, giảm thiểu tối đa rủi ro thuốc quá hạn.
4. **Trợ lý AI & Guardrails Dược học:** Hỗ trợ dược sĩ tra cứu tương tác thuốc, liều dùng; thiết lập nguyên tắc an toàn y tế từ chối chẩn đoán bệnh thay bác sĩ.
5. **Dashboard Tổng quan:** Theo dõi số lượng mặt hàng, hóa đơn bán ra và trạng thái vận hành của hệ thống.

---

## 🛠️ Hướng Dẫn Cài Đặt & Khởi Chạy

### 1. Yêu cầu môi trường
- Python >= 3.11
- Node.js >= 18.x và npm

---

### 2. Cài đặt và Chạy Backend

1. **Mở Terminal và điều hướng vào thư mục backend:**
   ```bash
   cd backend