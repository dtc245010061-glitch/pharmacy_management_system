# Codebase Map - Pharmacy AI System

pharmacy_ai_system/
|── docs/
|     |──system_analysis_and_design.md  # Tài liệu Phân tích & Thiết kế
|     |──ai_collaboration_log_phase1.md # Nhật ký minh chứng dùng AI
|
|
|
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py             # API Đăng nhập, xác thực và cấp phát JWT token
│   │   │   │   ├── categories.py       # API CRUD Danh mục thuốc
│   │   │   │   ├── medicines.py        # API CRUD Thuốc, kiểm tra tồn kho & upload file ảnh
│   │   │   │   ├── batches.py          # API Quản lý lô thuốc và ngày hết hạn phục vụ FEFO
│   │   │   │   ├── invoices.py         # API Bán hàng, xuất hóa đơn và xử lý trừ kho FEFO
│   │   │   │   └── ai.py               # API Tích hợp Google GenAI SDK (gemini-2.5-flash) có Guardrail
│   │   │   └── router.py               # Tổng hợp các endpoint vào api_router
│   │   ├── core/
│   │   │   ├── config.py               # Cấu hình biến môi trường và settings hệ thống
│   │   │   ├── database.py             # Khởi tạo SQLAlchemy Engine, SessionLocal, get_db
│   │   │   └── security.py             # Hàm băm mật khẩu (bcrypt) và tạo/giải mã JWT
│   │   ├── models/
│   │   │   └── models.py               # Khai báo cấu trúc bảng CSDL (User, Medicine, Category, Batch, Invoice, InvoiceItem)
│   │   ├── schemas/
│   │   │   └── schemas.py              # Định nghĩa Pydantic schemas validate dữ liệu Request/Response
│   │   └── main.py                     # Điểm khởi động FastAPI app, cấu hình CORS, Mount static files (/uploads)
│   ├── uploads/                        # Thư mục lưu trữ ảnh tải lên (local storage)
│   │   └── medicines/
|   ├── .env.example                    # 
│   ├── .env                            # Lưu trữ API Key, SECRET_KEY và thông tin nhạy cảm
│   ├── requirements.txt                # Danh sách dependencies của Backend
│   └── pharmacy.db                     # File cơ sở dữ liệu SQLite cục bộ
│
├── frontend/
│   ├── public/                         # Tài nguyên tĩnh của ứng dụng Vue
│   ├── src/
│   │   ├── assets/                     # File CSS, Icons, Fonts
│   │   ├── components/                 # Các UI Component dùng chung (Navbar, Card, Modal,...)
│   │   ├── services/
│   │   │   └── api.js                  # Cấu hình Axios instance kèm Interceptor tự động gắn Bearer Token
│   │   ├── views/
│   │   │   ├── Login.vue               # Màn hình đăng nhập hệ thống
│   │   │   ├── Dashboard.vue           # Màn hình Trang chủ thống kê tổng quan
│   │   │   ├── Medicines.vue           # Màn hình Quản lý danh mục, thêm thuốc và tải ảnh
│   │   │   ├── POS.vue                 # Màn hình Quầy bán thuốc tự động trừ kho FEFO
│   │   │   └── AIChat.vue              # Màn hình Chatbot Dược sĩ tương tác với Gemini AI
│   │   ├── router/
│   │   │   └── index.js                # Cấu hình định tuyến Vue Router & Navigation Guards kiểm tra Auth
│   │   ├── App.vue                     # Root Component
│   │   └── main.js                     # Entry point của Frontend Vue 3
│   ├── index.html                      # HTML template chính
│   ├── package.json                    # Khai báo dependencies của Frontend
│   └── vite.config.js                  # Cấu hình Vite dev server
│
├── .gitignore                          # Chặn đẩy các file nhạy cảm (.env, *.db, uploads/node_modules/) lên Git
├── architecture.md                     # Tài liệu kiến trúc hệ thống
├── codebase-map.md                     # Sơ đồ tổ chức mã nguồn
├── README.md                           #
├── user_stories.md                     # Danh sách User Stories
└── .geminirules                        # Quy tắc và hướng dẫn hoạt động dành cho AI Coding Agent