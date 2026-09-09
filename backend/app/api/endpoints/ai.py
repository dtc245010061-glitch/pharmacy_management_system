from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from google import genai
from google.genai import types
import os
import json
import re
import uuid
import shutil
from pathlib import Path
from datetime import date, timedelta
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import models

load_dotenv()

router = APIRouter()

UPLOAD_DIR = Path("uploads/medicines")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class AIQueryRequest(BaseModel):
    prompt: str

class InteractionCheckRequest(BaseModel):
    medicines: List[str]

@router.post("/consult")
def consult_ai(request: AIQueryRequest, db: Session = Depends(get_db)):
    """
    Trợ lý AI Dược học kết hợp dữ liệu kho thuốc nội bộ theo thời gian thực (RAG thu nhỏ).
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Thiếu cấu hình API Key.")
        
        client = genai.Client(api_key=api_key)
        
        medicines = (
            db.query(
                models.Medicine.id,
                models.Medicine.name,
                models.Medicine.unit,
                models.Medicine.description
            )
            .limit(100)
            .all()
        )

        batch_stocks = (
            db.query(
                models.Batch.medicine_id,
                func.sum(models.Batch.quantity).label("total_qty")
            )
            .filter(models.Batch.quantity > 0)
            .group_by(models.Batch.medicine_id)
            .all()
        )
        stock_map = {row.medicine_id: (row.total_qty or 0) for row in batch_stocks}

        med_summary = []
        for m in medicines:
            stock_qty = stock_map.get(m.id, 0)
            med_summary.append(f"- {m.name}: Tồn kho {stock_qty} {m.unit or 'đơn vị'} (Mô tả: {m.description or 'Không'})")
        inventory_context = "\n".join(med_summary) if med_summary else "Kho hiện chưa có danh mục thuốc."

        batches = (
            db.query(
                models.Batch.batch_number,
                models.Batch.quantity,
                models.Batch.expiry_date,
                models.Medicine.name,
                models.Medicine.unit
            )
            .join(models.Medicine, models.Batch.medicine_id == models.Medicine.id)
            .filter(models.Batch.quantity > 0)
            .order_by(models.Batch.expiry_date.asc())
            .limit(30)
            .all()
        )
        batch_summary = []
        for batch_num, b_qty, exp_date, m_name, m_unit in batches:
            batch_summary.append(f"- Lô {batch_num} ({m_name}): Còn {b_qty} {m_unit or 'đơn vị'}, HSD: {exp_date}")
        batches_context = "\n".join(batch_summary) if batch_summary else "Hiện chưa có thông tin lô hàng."

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
            model='gemini-3.6-flash',
            contents=f"{system_instruction}\n\nCâu hỏi từ người dùng: {request.prompt}"
        )
        
        return {"response": response.text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kết nối tới trợ lý AI: {str(e)}")

@router.post("/check-interactions")
def check_drug_interactions(request: InteractionCheckRequest):
    """
    Phân tích tương tác chéo giữa các loại thuốc trong giỏ hàng POS (AI Guardrail).
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
2. Trả về DUY NHẤT một chuỗi JSON hợp lệ (không kèm Markdown block) theo cấu trúc:
{{
    "has_interaction": true hoặc false,
    "severity": "safe" | "warning" | "danger",
    "summary": "Tóm tắt ngắn gọn 1-2 câu về tương tác chính",
    "details": "Chi tiết cơ chế tương tác, rủi ro cụ thể và hướng xử lý"
}}
"""
        response = client.models.generate_content(
            model='gemini-3.6-flash',
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

@router.post("/scan-medicine-image")
async def scan_medicine_image(file: UploadFile = File(...)):
    """
    AI Vision: Phân tích ảnh vỏ hộp / bao bì thuốc bằng Gemini Flash Multimodal,
    tự động trích xuất các trường thông tin chuẩn GPP để điền vào form thuốc mới.
    """
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Thiếu cấu hình GEMINI_API_KEY.")

        client = genai.Client(api_key=api_key)

        # 1. Lưu file ảnh vào thư mục upload
        file_ext = Path(file.filename).suffix or ".jpg"
        unique_name = f"scan_{uuid.uuid4().hex[:10]}{file_ext}"
        save_path = UPLOAD_DIR / unique_name

        image_bytes = await file.read()
        with open(save_path, "wb") as buffer:
            buffer.write(image_bytes)

        image_url = f"/uploads/medicines/{unique_name}"

        # 2. Tạo prompt yêu cầu AI Vision trích xuất thông tin
        prompt = """
Bạn là chuyên gia AI Dược học thị giác chuyên đọc và phân tích bao bì thuốc tân dược chuẩn GPP.
Hãy đọc kỹ hình ảnh bao bì / vỏ hộp thuốc được cung cấp và trích xuất các thông tin sau:

YÊU CẦU:
1. Trích xuất chính xác, trung thực các trường thông tin nhìn thấy được trên bao bì.
2. Trả về DUY NHẤT một chuỗi JSON hợp lệ (không kèm Markdown code block hay văn bản khác) theo cấu trúc:
{
    "name": "Tên thương mại của thuốc kèm hàm lượng chính (ví dụ: Panadol Extra 500mg/65mg)",
    "registration_number": "Số đăng ký lưu hành nếu thấy (ví dụ: VD-25219-16 hoặc VN-...)",
    "ingredients": "Thành phần hoạt chất và hàm lượng (ví dụ: Paracetamol 500mg, Caffeine 65mg)",
    "dosage_form": "Dạng bào chế (ví dụ: Viên nén bao phim, Viên nang mềm, Gói bột pha hỗn dịch uống...)",
    "packaging": "Quy cách đóng gói (ví dụ: Hộp 15 vỉ x 12 viên, Chai 100ml...)",
    "unit": "Đơn vị tính cơ bản nhất (Hộp, Vỉ, Viên, Chai, Ống, Gói)",
    "manufacturer": "Tên công ty sản xuất",
    "country": "Nước sản xuất (ví dụ: Việt Nam, Pháp, Ấn Độ...)",
    "category_suggestion": "Gợi ý phân loại nhóm thuốc (ví dụ: Giảm đau - Hạ sốt, Kháng sinh, Tiêu hóa...)",
    "expiry_date": "Hạn sử dụng ở định dạng YYYY-MM-DD nếu thấy trên ảnh (hoặc null nếu không thấy)",
    "estimated_price": 0.0,
    "description": "Tóm tắt ngắn gọn 1-2 câu về công dụng chính, chỉ định và chống chỉ định quan trọng"
}
"""

        # 3. Gửi ảnh trực tiếp tới Gemini 3.6 Flash
        mime_type = file.content_type or "image/jpeg"
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

        response = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[image_part, prompt]
        )

        raw_text = response.text.strip()
        cleaned_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.MULTILINE).strip()

        try:
            parsed_data = json.loads(cleaned_text)
        except json.JSONDecodeError:
            parsed_data = {
                "name": "",
                "description": raw_text
            }

        parsed_data["image_url"] = image_url
        return parsed_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi AI Vision đọc ảnh thuốc: {str(e)}")