# User Stories - Hệ Thống Quản Lý Nhà Thuốc AI (Pharmacy AI System)

## 1. Xác thực & Quản lý người dùng (Authentication & Authorization)
- **US-01:** Là Dược sĩ / Quản lý, tôi muốn đăng nhập bằng tài khoản (username/password) để truy cập vào hệ thống an toàn và nhận JWT Token.
- **US-02:** Là Người dùng, tôi muốn đăng xuất khỏi hệ thống để bảo mật phiên làm việc trên trình duyệt.

## 2. Quản lý Danh mục & Kho thuốc (Inventory & Catalog Management)
- **US-03:** Là Dược sĩ, tôi muốn thêm mới thông tin thuốc (Tên thuốc, Đơn vị tính, Số lượng, ID danh mục, Mô tả) để cập nhật danh mục kho.
- **US-04:** Là Dược sĩ, tôi muốn tải ảnh thuốc lên hệ thống để dễ dàng nhận diện sản phẩm trực quan trên giao diện quầy thuốc.
- **US-05:** Là Dược sĩ, tôi muốn xem danh sách toàn bộ các loại thuốc hiện có kèm số lượng tồn kho và ảnh minh họa.
- **US-06:** Là Dược sĩ, tôi muốn tìm kiếm thuốc theo tên để tra cứu nhanh thông tin tồn kho.
- **US-07:** Là Quản lý, tôi muốn xóa thuốc khỏi hệ thống khi sản phẩm ngừng kinh doanh.

## 3. Quầy bán hàng & Tự động hóa FEFO (Point of Sale - POS)
- **US-08:** Là Dược sĩ, tôi muốn tạo đơn bán hàng và xuất kho thuốc cho khách.
- **US-09:** Là Hệ thống, tôi tự động ưu tiên xuất các lô thuốc có hạn sử dụng gần nhất trước (thuật toán FEFO - First Expired, First Out) để giảm thiểu rủi ro thuốc hết hạn.
- **US-10:** Là Dược sĩ, tôi muốn xem lại danh sách các hóa đơn đã xuất kèm chi tiết mặt hàng và doanh thu.

## 4. Trợ lý Dược học AI & Kiểm duyệt Guardrail (AI Consultation)
- **US-11:** Là Dược sĩ, tôi muốn gửi câu hỏi tra cứu tương tác thuốc, chỉ định và liều dùng tới Trợ lý AI (Google Gemini).
- **US-12:** Là Hệ thống AI, tôi áp dụng Guardrails y khoa để từ chối đưa ra chẩn đoán thay thế bác sĩ, đồng thời cảnh báo rủi ro tương tác thuốc nghiêm trọng nhằm đảm bảo an toàn cho bệnh nhân.

## 5. Bảng điều khiển Tổng quan (Dashboard)
- **US-13:** Là Quản lý, tôi muốn xem các chỉ số thống kê nhanh (Tổng loại thuốc, Số hóa đơn đã bán, Trạng thái hệ thống AI) ngay khi đăng nhập vào hệ thống.