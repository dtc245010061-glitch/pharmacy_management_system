from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from google import genai
import os
import json
import re
from datetime import date, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import models

# Tải các biến từ file .env
load_dotenv()

router = APIRouter()

class AIQueryRequest(BaseModel):
    prompt: str

class InteractionCheckRequest(BaseModel):
    medicines: List[str]

@router.post("/consult")
def consult_ai(request: AIQueryRequest, db: Session = Depends(get_db)):
    """
    Trợ lý AI Dược học kết hợp dữ liệu kho thuốc nội bộ theo thời gian thực (RAG thu nhỏ).
    Có khả năng vừa trả lời chuyên môn y dược vừa tra cứu chính xác số lượng tồn và HSD các lô thuốc.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Thiếu cấu hình API Key.")
        
        client = genai.Client(api_key=api_key)
        
        # 1. Thu thập dữ liệu kho thuốc hiện có
        medicines = db.query(models.Medicine).limit(100).all()
        med_summary = []
        for m in medicines:
            med_summary.append(f"- {m.name}: Tồn kho {m.quantity or 0} {m.unit} (Mô tả: {m.description or 'Không'})")
        inventory_context = "\n".join(med_summary) if med_summary else "Kho hiện chưa có danh mục thuốc."

        # 2. Thu thập dữ liệu các lô hàng còn tồn kho xếp theo FEFO (hạn dùng gần nhất lên đầu)
        batches = (
            db.query(models.Batch, models.Medicine.name, models.Medicine.unit)
            .join(models.Medicine, models.Batch.medicine_id == models.Medicine.id)
            .filter(models.Batch.quantity > 0)
            .order_by(models.Batch.expiry_date.asc())
            .limit(30)
            .all()
        )
        batch_summary = []
        for b, m_name, m_unit in batches:
            batch_summary.append(f"- Lô {b.batch_number} ({m_name}): Còn {b.quantity} {m_unit}, HSD: {b.expiry_date}")
        batches_context = "\n".join(batch_summary) if batch_summary else "Hiện chưa có thông tin lô hàng."

        # 3. Thiết lập System Instruction kết hợp dữ liệu thực tế
        system_instruction = (
            "Bạn là trợ lý AI chuyên gia y tế và quản lý dược học cho hệ thống nhà thuốc.\n"
            "DƯỚI ĐÂY LÀ DỮ LIỆU THỰC TẾ TRONG KHO THUỐC CỦA NHÀ THUỐC HIỆN TẠI:\n\n"
            f"[DANH MỤC THUỐC & TỒN KHO]:\n{inventory_context}\n\n"
            f"[CÁC LÔ HÀNG ĐANG CÒN HÀNG (SẮP XẾP THEO FEFO - HSD GẦN NHẤT ĐẾN XA NHẤT)]:\n{batches_context}\n\n"
            "NGUYÊN TẮC TRẢ LỜI:\n"
            "1. Nếu người dùng hỏi về số lượng tồn kho, tình trạng thuốc hay các lô thuốc sắp hết hạn: "
            "hãy tra cứu và trả lời chính xác dựa trên dữ liệu thực tế đã cung cấp ở trên. Tuyệt đối không bịa số liệu kho.\n"
            "2. Nếu người dùng hỏi về kiến thức chuyên môn y dược, tương tác thuốc, chỉ định, liều dùng: "
            "hãy cung cấp thông tin chuẩn y khoa, chính xác, dễ hiểu và luôn nhắc nhở tuân theo chỉ định của bác sĩ.\n"
            "3. Luôn giữ thái độ chuyên nghiệp, ngắn gọn và rõ ràng."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system_instruction}\n\nCâu hỏi từ người dùng: {request.prompt}"
        )
        
        return {"response": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kết nối tới trợ lý AI: {str(e)}")

@router.post("/check-interactions")
def check_drug_interactions(request: InteractionCheckRequest):
    """
    Phân tích tương tác chéo giữa các loại thuốc trong giỏ hàng trước khi xuất đơn.
    Trả về định dạng JSON có cấu trúc để hiển thị huy hiệu cảnh báo trên giao diện POS.
    """
    if len(request.medicines) < 2:
        return {
            "has_interaction": False,
            "severity": "safe",
            "summary": "Đơn thuốc có dưới 2 loại thuốc, không phát sinh tương tác chéo.",
            "details": "Đơn thuốc an toàn để thanh toán."
        }

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Thiếu cấu hình API Key.")

        client = genai.Client(api_key=api_key)

        prompt = f"""
Bạn là hệ thống AI Dược lâm sàng chuyên sâu về an toàn đơn thuốc (Drug Interaction Guardrail).
Hãy phân tích tương tác chéo giữa danh sách các loại thuốc sau trong cùng một đơn:
{', '.join(request.medicines)}

YÊU CẦU:
1. Đánh giá xem giữa các thuốc này có tương tác đối kháng, tăng độc tính, trùng lặp hoạt chất hoặc chống chỉ định nguy hiểm hay không.
2. Trả về DUY NHẤT một chuỗi JSON hợp lệ (không kèm Markdown code block hay giải thích ngoài JSON) theo đúng cấu trúc sau:
{{
    "has_interaction": true hoặc false,
    "severity": "safe" (an toàn) | "warning" (cần lưu ý/theo dõi) | "danger" (nguy hiểm/chống chỉ định),
    "summary": "Tóm tắt ngắn gọn 1-2 câu về tương tác chính",
    "details": "Chi tiết cơ chế tương tác, rủi ro cụ thể và hướng xử lý/thay thế cho dược sĩ"
}}
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )

        raw_text = response.text.strip()
        cleaned_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            result = json.loads(cleaned_text)
        except json.JSONDecodeError:
            result = {
                "has_interaction": True,
                "severity": "warning",
                "summary": "Đã phát hiện thông tin tương tác cần chú ý.",
                "details": raw_text
            }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi phân tích tương tác thuốc: {str(e)}")