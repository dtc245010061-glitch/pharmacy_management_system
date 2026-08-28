from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
import os
from dotenv import load_dotenv

# Tải các biến từ file .env
load_dotenv()

router = APIRouter()

class AIQueryRequest(BaseModel):
    prompt: str

@router.post("/consult")
def consult_ai(request: AIQueryRequest):
    try:
        # Đọc Key an toàn từ biến môi trường
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