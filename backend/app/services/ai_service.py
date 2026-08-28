from google import genai
from app.core.config import settings

# Khởi tạo client theo chuẩn thư viện mới
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# Rào chắn 1: Các từ khóa cấm để chặn sớm ở Backend trước khi gọi AI
FORBIDDEN_KEYWORDS = ["chữa bệnh", "uống mấy viên", "đau bụng", "trị bệnh", "đơn thuốc", "kê đơn"]

SYSTEM_PROMPT = """
Bạn là trợ lý nội bộ nhà thuốc. Không đưa lời khuyên điều trị, không chỉ định liều dùng ngoài dữ liệu được cung cấp.
Nếu người dùng hỏi về cách chữa bệnh hoặc liều lượng không có trong dữ liệu, hãy từ chối trả lời.
"""

def check_guardrail_input(query: str) -> bool:
    """Kiểm tra xem câu hỏi có chứa từ khóa cấm tư vấn y tế không."""
    query_lower = query.lower()
    for word in FORBIDDEN_KEYWORDS:
        if word in query_lower:
            return False
    return True

def generate_ai_response(query: str, context_data: str, context_type: str) -> str:
    """
    Xử lý gọi Gemini API dựa trên context.
    """
    if not check_guardrail_input(query):
        return "Yêu cầu bị từ chối: Trợ lý AI không được phép đưa ra lời khuyên điều trị hay kê đơn."

    # Xây dựng Prompt dựa trên nghiệp vụ
    if context_type == "medicine_info":
        prompt = f"{SYSTEM_PROMPT}\nUser: Dữ liệu thuốc: {context_data}. Hãy tóm tắt thông tin để nhân viên tra cứu nhanh: {query}"
    elif context_type == "sop":
        prompt = f"{SYSTEM_PROMPT}\nUser: Quy trình nội bộ: {context_data}. Hãy giải đáp thắc mắc sau: {query}"
    elif context_type == "expiry_report":
        prompt = f"{SYSTEM_PROMPT}\nUser: Dữ liệu thuốc sắp hết hạn: {context_data}. Hãy sinh báo cáo và đề xuất xử lý: {query}"
    else:
        prompt = f"{SYSTEM_PROMPT}\nUser: {query}"

    try:
        # Cú pháp generate_content mới
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Lỗi khi kết nối với AI: {str(e)}"