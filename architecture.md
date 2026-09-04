# Architecture Specification - Pharmacy AI System

## 1. Kiến trúc Tổng thể
Hệ thống được xây dựng theo mô hình **Client-Server** phân tách độc lập:
- **Frontend:** Single Page Application (SPA) phát triển bằng **Vue 3** và **Vite**.
- **Backend:** RESTful API phát triển bằng **FastAPI (Python 3.11+)**.
- **Cơ sở dữ liệu:** **SQLite** quản lý thông qua ORM **SQLAlchemy**.
- **AI Engine:** Tích hợp SDK **google-genai** (Model: `gemini-2.5-flash`).

```text
[Trình duyệt Dược sĩ]
       |
  (HTTP / JSON)
       v
[Vue 3 SPA (Port 3000)]
       |
 (Axios REST API / Multipart Form-Data)
       v
[FastAPI Backend (Port 8000)]
  ├── CORS Middleware (Xử lý giao tiếp Cross-Origin)
  ├── Static Files Handler (/uploads/medicines)
  ├── JWT Authentication Layer
  ├── Business Logic (FEFO Algorithm)
  └── Services:
        ├── SQLite DB via SQLAlchemy (Lưu trữ Dữ liệu giao dịch & Kho)
        └── Google GenAI Client (gemini-2.5-flash) (Tư vấn Dược & Guardrail)