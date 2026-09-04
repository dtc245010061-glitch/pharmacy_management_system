# TÀI LIỆU PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG
## DỰ ÁN: HỆ THỐNG QUẢN LÝ NHÀ THUỐC TÍCH HỢP AI (PHARMACY AI SYSTEM)

---

## 1. PHÂN TÍCH BÀI TOÁN QUẢN LÝ (Tiêu chí 1)

### 1.1. Bối cảnh và Vấn đề thực tế
- **Thực trạng:** Các nhà thuốc truyền thống gặp khó khăn lớn trong việc theo dõi hạn sử dụng của hàng trăm loại thuốc, dẫn đến rủi ro thuốc hết hạn bị tiêu hủy gây tổn thất chi phí, hoặc vô tình bán thuốc cận hạn cho khách hàng.
- **Nghiệp vụ xuất kho:** Thường bị nhầm lẫn giữa FIFO (Vào trước ra trước) và FEFO (Hết hạn trước ra trước). Với ngành y tế và dược phẩm, **FEFO (First Expired, First Out)** là tiêu chuẩn bắt buộc.
- **Tra cứu thông tin:** Nhân viên bán thuốc cần tra cứu nhanh tương tác thuốc, chống chỉ định, nhưng việc đọc dược thư giấy rất mất thời gian. Nếu áp dụng AI không cẩn trọng, AI có thể sinh phản hồi sai lệch (hallucination) gây nguy hiểm.
- **Giải pháp:** Xây dựng hệ thống quản trị nhà thuốc thông minh, tự động hóa xuất kho theo lô cận hạn (FEFO) và tích hợp Trợ lý AI có Guardrails kiểm soát nghiêm ngặt.

### 1.2. Đối tượng sử dụng (Actors)
1. **Quản lý (Admin):** Quản trị danh mục, nhân sự, xem báo cáo doanh thu, kho và giám sát toàn bộ hoạt động.
2. **Dược sĩ chuyên môn (Pharmacist):** Nhập lô hàng, kiểm soát chất lượng, tra cứu tương tác thuốc và quy trình nội bộ thông qua AI.
3. **Thu ngân (Cashier):** Thực hiện thao tác bán thuốc tại quầy (POS), tạo hóa đơn cho khách.

---

## 2. YÊU CẦU CHỨC NĂNG (Tiêu chí 2)

### Bảng đặc tả chi tiết Chức năng Quản lý (Input - Processing - Output)

| Mã CN | Tên Chức Năng | Dữ liệu Đầu vào (Input) | Quy trình Xử lý (Processing) | Dữ liệu Đầu ra (Output) |
| :--- | :--- | :--- | :--- | :--- |
| **F-01** | Đăng nhập & Xác thực | Username, Password | Kiểm tra tài khoản, xác thực mật khẩu qua bcrypt, tạo JWT Token kèm `role`. | JWT Token, phiên làm việc hợp lệ. |
| **F-02** | Quản lý Thuốc & Danh mục | Tên thuốc, đơn vị, danh mục, mô tả, ảnh | Validate dữ liệu, lưu vào bảng `medicines`, lưu trữ file ảnh vào `/uploads/medicines`. | Bản ghi thuốc mới, danh sách thuốc có ảnh. |
| **F-03** | Quản lý Lô & Hạn sử dụng | Số lô, ID thuốc, ngày SX, HSD, giá nhập, số lượng | Validate ngày SX < HSD, tạo bản ghi `batches`. | Lô thuốc mới được ghi nhận vào kho. |
| **F-04** | Quản lý Nhà cung cấp | Tên NCC, SĐT, địa chỉ, mã số thuế | Kiểm tra trùng lặp mã/tên, lưu vào bảng `suppliers`. | Danh sách nhà cung cấp thuốc. |
| **F-05** | Bán hàng & Trừ kho FEFO | ID khách hàng, danh sách thuốc và số lượng mua | 1. Quét bảng `batches` theo `medicine_id`.<br>2. Sắp xếp tăng dần theo `expiry_date`.<br>3. Trừ số lượng từng lô có hạn dùng gần nhất trước.<br>4. Tạo bản ghi `invoices` và `invoice_items`. | Hóa đơn bán hàng, số tồn kho các lô giảm tương ứng. |
| **F-06** | Cảnh báo Cận hạn / Tồn kho | Ngưỡng ngày cảnh báo (ví dụ 30 ngày), ngưỡng số lượng | Quét các lô có `expiry_date - CURRENT_DATE <= 30` hoặc thuốc có tổng tồn `< threshold`. | Danh sách thuốc cần xử lý xả hàng/hủy. |
| **F-07** | Tra cứu đa tiêu chí | Tên thuốc, nhóm thuốc, số lô, hạn dùng | Truy vấn kết hợp lọc SQL (JOIN medicines, categories, batches). | Danh sách kết quả phù hợp tiêu chí lọc. |
| **F-08** | Thống kê & Báo cáo | Khoảng thời gian thống kê (ngày/tháng) | Tổng hợp doanh thu từ `invoices`, đếm số thuốc sắp hết hạn, tính tổng giá trị kho. | Biểu đồ doanh thu, báo cáo tổng hợp. |

### Bảng đặc tả Chức năng AI

| Mã AI | Tên Chức Năng | Dữ liệu Đầu vào | Quy trình Xử lý | Dữ liệu Đầu ra |
| :--- | :--- | :--- | :--- | :--- |
| **AI-01** | Tóm tắt thông tin thuốc | Dữ liệu thuốc đã duyệt trong CSDL (thành phần, chỉ định, đơn vị) | Nạp vào System Prompt chuyên gia dược; yêu cầu tóm tắt ngắn gọn có Guardrail y tế. | Bản tóm tắt dễ hiểu cho nhân viên kèm khuyến cáo an toàn. |
| **AI-02** | Báo cáo thuốc sắp hết hạn | Danh sách các lô thuốc có HSD cận kề được trích xuất từ DB | AI phân tích số lượng tồn và ngày hết hạn, đề xuất phương án (khuyến mãi, trả NCC, tiêu hủy). | Báo cáo đề xuất xử lý lô hàng chi tiết. |
| **AI-03** | Chatbot hỏi đáp quy trình | Câu hỏi của nhân viên + Tài liệu quy trình nội bộ (SOP) | Đối soát câu hỏi với quy trình chuẩn GPP, từ chối trả lời ngoài phạm vi. | Hướng dẫn thực hiện quy trình chuẩn xác. |

---

## 3. YÊU CẦU PHI CHỨC NĂNG (Tiêu chí 3)

1. **Bảo mật (Security):**
   - Mật khẩu người dùng được băm 1 chiều bằng thuật toán `bcrypt`.
   - Cơ chế ủy quyền thông qua `JSON Web Token (JWT)` với thuật toán HS256, thời hạn 24 giờ.
   - API Key của Gemini AI được bảo vệ tuyệt đối bằng biến môi trường `.env`, không bao giờ được commit lên Git.
   - Kiểm soát phân quyền dựa trên vai trò (Role-Based Access Control - RBAC).
2. **Hiệu năng (Performance):**
   - Các API truy vấn CSDL phản hồi dưới 300ms với tập dữ liệu thông thường.
   - API gọi Trợ lý AI phản hồi trong khoảng 1.5s - 3.5s (tối ưu bằng model `gemini-2.5-flash`).
3. **Độ khả dụng & Sao lưu (Availability & Backup):**
   - Hệ thống sẵn sàng phục vụ 99.5%.
   - Cơ sở dữ liệu SQLite hỗ trợ tạo bản sao lưu tự động định kỳ hàng ngày dạng file timestamp snapshot.
4. **Trải nghiệm người dùng (UX/UI):**
   - Giao diện phát triển bằng Vue 3, phản hồi trực quan với trạng thái Loading, Toast thông báo thành công hoặc bắt lỗi rõ ràng.

---

## 4. THIẾT KẾ ACTOR VÀ USE CASE (Tiêu chí 4)

### 4.1. Ma trận Phân quyền theo Vai trò

| Chức năng / Quyền hạn       | Quản lý (Admin) | Dược sĩ (Pharmacist) | Thu ngân (Cashier) |
| :--- | :---: | :---: | :---: |
| Quản lý tài khoản & Phân quyền        | ✅ |        ❌ |                  ❌ |
| Xem báo cáo doanh thu tổng quan       | ✅ |        ❌ |                  ❌ |
| Quản lý Nhà cung cấp                  | ✅ |        ✅ |                  ❌ |
| Quản lý Thuốc, Danh mục & Nhập lô     | ✅ |        ✅ |                  ❌ |
| Tra cứu thuốc & Sử dụng Trợ lý AI     | ✅ |        ✅ |                  ✅ |
| Bán thuốc tại quầy (POS) & In hóa đơn | ✅ |        ✅ |                  ✅ |

### 4.2. Sơ đồ Use Case Hệ thống

```mermaid
graph LR
    Admin[Quản lý]
    Pharmacist[Dược sĩ]
    Cashier[Thu ngân]

    subgraph "Hệ Thống Quản Lý Nhà Thuốc AI"
        UC1(Đăng nhập / Đăng xuất)
        UC2(Quản lý Thuốc & Danh mục)
        UC3(Quản lý Lô & Hạn sử dụng)
        UC4(Quản lý Nhà cung cấp)
        UC5(Bán hàng xuất kho FEFO)
        UC6(Xem Báo cáo Doanh thu & Cận hạn)
        UC7(Tra cứu thông tin thuốc với AI)
        UC8(Sinh đề xuất xử lý lô cận hạn bằng AI)
        UC9(Hỏi đáp quy trình nội bộ bằng AI)
    end

    Admin --> UC1
    Admin --> UC2
    Admin --> UC3
    Admin --> UC4
    Admin --> UC5
    Admin --> UC6
    Admin --> UC7
    Admin --> UC8
    Admin --> UC9

    Pharmacist --> UC1
    Pharmacist --> UC2
    Pharmacist --> UC3
    Pharmacist --> UC4
    Pharmacist --> UC5
    Pharmacist --> UC7
    Pharmacist --> UC8
    Pharmacist --> UC9

    Cashier --> UC1
    Cashier --> UC5
    Cashier --> UC7