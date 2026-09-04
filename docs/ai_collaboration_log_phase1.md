ACTION: -CREATE
REASON: Nhật ký minh chứng sử dụng AI trong giai đoạn phân tích và thiết kế, ghi rõ vai trò Người ra quyết định và cách kiểm chứng kết quả của AI (Đáp ứng Tiêu chí 9).
```markdown
# NHẬT KÝ MINH CHỨNG SỬ DỤNG AI TRONG SDLC (GIAI ĐOẠN 1)
## PHÂN TÍCH YÊU CẦU & THIẾT KẾ HỆ THỐNG (Tiêu chí 9)

> **Nguyên tắc phối hợp:** 
> - Sinh viên giữ vai trò **Chủ dự án / Người ra quyết định cuối cùng (Decision Maker)**.
> - AI (Google Gemini) giữ vai trò **Coding & Architectural Assistant**. 
> - Mọi kết quả do AI sinh ra đều phải trải qua bước kiểm chứng, đối chiếu tiêu chuẩn y tế GPP và tinh chỉnh lại.

---

### Phiên làm việc 1: Phân tích Nghiệp vụ Xuất kho và Thuật toán FEFO
* **Mục tiêu:** Xác định logic xuất kho chuẩn xác cho nhà thuốc có quản lý hạn dùng.
* **Prompt gửi AI:**
  > "Tôi đang làm đề tài Quản lý nhà thuốc tích hợp AI. Hãy so sánh việc dùng thuật toán FIFO và FEFO trong xuất kho thuốc. Khi thiết kế CSDL, tôi cần các bảng nào để quản lý hạn sử dụng chính xác đến từng lô?"
* **Phản hồi của AI:**
  > AI đề xuất sử dụng FEFO (First Expired, First Out) vì thuốc nhập sau vẫn có thể hết hạn trước thuốc nhập trước. AI gợi ý tạo một bảng `batches` riêng biệt liên kết với `medicines` bằng khóa ngoại `medicine_id`, lưu trữ `expiry_date` và `current_quantity`.
* **Kiểm chứng & Tinh chỉnh của Sinh viên (Human Verification):**
  - *Nhận xét:* AI đề xuất đúng bản chất bài toán dược phẩm.
  - *Chỉnh sửa:* Bổ sung thêm quan hệ giữa `batches` với `suppliers` (Nhà cung cấp) để phục vụ cho việc đổi trả thuốc cận hạn mà AI chưa nghĩ tới; thêm ràng buộc `expiry_date > manufacturing_date`.

---

### Phiên làm việc 2: Thiết kế Giới hạn an toàn (Guardrails) cho AI Tra cứu Thuốc
* **Mục tiêu:** Xây dựng System Prompt an toàn, loại bỏ nguy cơ AI tư vấn y khoa sai lệch hoặc vi phạm pháp luật.
* **Prompt gửi AI:**
  > "Thiết kế một System Prompt cho chatbot nội bộ nhà thuốc. Làm thế nào để ngăn chặn tuyệt đối việc AI đưa ra lời khuyên kê đơn hay tự chẩn đoán bệnh thay bác sĩ khi nhân viên nhập câu hỏi nhạy cảm?"
* **Phản hồi của AI:**
  > AI cung cấp cấu trúc Prompt 3 phần: (1) Vai trò trợ lý tham khảo, (2) Danh sách từ khóa cấm (chẩn đoán, kê liều cho trẻ sơ sinh, thay thế phác đồ điều trị), (3) Câu trả lời mặc định khi vượt phạm vi.
* **Kiểm chứng & Tinh chỉnh của Sinh viên (Human Verification):**
  - *Nhận xét:* Cấu trúc tốt nhưng quá dài dòng, dễ gây tốn token và tăng độ trễ.
  - *Chỉnh sửa:* Rút gọn System Prompt lại thành các điều khoản mệnh lệnh súc tích, bổ sung bắt buộc dòng cảnh báo: `[CẢNH BÁO]: Thông tin tra cứu nội bộ, cần có chỉ định của bác sĩ/dược sĩ` vào cuối tất cả câu trả lời của API `/ai/consult`.

---

### Phiên làm việc 3: Phản biện Kiến trúc và Cơ chế Upload Ảnh Thuốc
* **Mục tiêu:** Lựa chọn phương án lưu trữ ảnh thuốc khi phát triển bằng FastAPI và Vue 3.
* **Prompt gửi AI:**
  > "FastAPI nên xử lý upload ảnh thuốc lưu thẳng vào SQLite dưới dạng BLOB (Base64) hay lưu file vào ổ cứng local rồi lưu đường dẫn (URL) vào database? Phương án nào tối ưu hơn?"
* **Phản hồi của AI:**
  > AI phân tích: Lưu Base64/BLOB vào SQLite sẽ làm phình to kích thước file CSDL rất nhanh, khiến backup chậm và giảm hiệu năng đọc ghi. Giải pháp tối ưu là lưu file vào thư mục `uploads/medicines/` trên server, dùng `StaticFiles` của FastAPI để phục vụ URL, và chỉ lưu chuỗi đường dẫn trong CSDL.
* **Kiểm chứng & Tinh chỉnh của Sinh viên (Human Verification):**
  - *Nhận xét:* Hoàn toàn chính xác với nguyên lý kiến trúc ứng dụng web.
  - *Chỉnh sửa:* Yêu cầu AI bổ sung cơ chế đổi tên file ảnh theo ID thuốc (`medicine_{id}.ext`) để tránh xung đột tên file khi người dùng upload nhiều file cùng tên.