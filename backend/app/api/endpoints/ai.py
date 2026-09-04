from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from google import genai
import os
import json
import re
from dotenv import load_dotenv

# Tải các biến từ file .env
load_dotenv()

router = APIRouter()

class AIQueryRequest(BaseModel):
    prompt: str

class InteractionCheckRequest(BaseModel):
    medicines: List[str]

@router.post("/consult")
def consult_ai(request: AIQueryRequest):
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Thiếu cấu hình API Key.")
        
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "Bạn là trợ lý AI chuyên gia y tế và dược học cho hệ thống nhà thuốc. "
            "Nhiệm vụ của bạn là hỗ trợ dược sĩ tra cứu thông tin thuốc, liều dùng và cảnh báo tương tác thuốc nguy hiểm. "
            "Luôn đặt sự an toàn của bệnh nhân lên hàng đầu, từ chối đưa ra chẩn đoán thay thế bác sĩ."
        )
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system_instruction}\n\nCâu hỏi từ dược sĩ: {request.prompt}"
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
        # Loại bỏ bọc code markdown nếu có
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