from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.models import models
from app.schemas import schemas

def process_checkout(db: Session, request: schemas.CheckoutRequest) -> models.Invoice:
    """
    Thuật toán xử lý giỏ hàng:
    1. Lặp qua từng mặt hàng trong giỏ.
    2. Tìm các lô còn hạn và còn tồn kho của thuốc đó, sắp xếp theo hạn dùng tăng dần (FEFO).
    3. Trừ dần số lượng vào các lô. Nếu lô hiện tại không đủ, trừ sạch lô này và chuyển sang lô tiếp theo.
    4. Lưu chi tiết hóa đơn với giá bán hardcopy.
    5. Rollback toàn bộ nếu có bất kỳ thuốc nào không đủ tổng tồn kho.
    """
    try:
        # Khởi tạo hóa đơn
        invoice = models.Invoice(user_id=request.user_id, total_amount=0.0)
        db.add(invoice)
        db.flush() # Đẩy xuống DB để lấy invoice.id (chưa commit)

        total_amount = 0.0

        for item in request.items:
            # Lấy các lô hàng hợp lệ (còn tồn và chưa hết hạn), dùng with_for_update() để khóa dòng (chống Race Condition khi nhiều người cùng bán)
            batches = db.query(models.Batch).filter(
                models.Batch.medicine_id == item.medicine_id,
                models.Batch.quantity > 0,
                models.Batch.expiry_date >= date.today()
            ).order_by(models.Batch.expiry_date.asc()).with_for_update().all()

            remain_qty = item.quantity
            
            for batch in batches:
                if remain_qty <= 0:
                    break # Đã trừ đủ số lượng cho mặt hàng này
                
                # Số lượng có thể trừ ở lô này
                deduct_qty = min(batch.quantity, remain_qty)
                
                # Cập nhật tồn kho lô
                batch.quantity -= deduct_qty
                remain_qty -= deduct_qty
                
                # Tính tiền và tạo chi tiết hóa đơn
                line_total = batch.sell_price * deduct_qty
                total_amount += line_total
                
                detail = models.InvoiceDetail(
                    invoice_id=invoice.id,
                    batch_id=batch.id,
                    quantity=deduct_qty,
                    price=batch.sell_price # Lưu cứng giá tại thời điểm bán
                )
                db.add(detail)
            
            # Nếu đã lặp qua tất cả lô mà vẫn còn số lượng cần mua (remain_qty > 0) -> Không đủ hàng
            if remain_qty > 0:
                raise ValueError(f"Thuốc ID {item.medicine_id} không đủ tồn kho hợp lệ (còn thiếu {remain_qty}).")

        # Cập nhật tổng tiền
        invoice.total_amount = total_amount
        db.commit() # Chốt giao dịch (Transaction hoàn thành)
        db.refresh(invoice)
        return invoice

    except Exception as e:
        db.rollback() # Hoàn tác toàn bộ thay đổi nếu có lỗi
        raise e