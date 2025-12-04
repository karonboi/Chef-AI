import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def identify_ingredients(image):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = """
    Hãy đóng vai một chuyên gia ẩm thực. Nhìn vào bức ảnh này và liệt kê tất cả các nguyên liệu thực phẩm có thể nhìn thấy.
    Bỏ qua các vật dụng không phải thực phẩm.
    Trả về kết quả dưới dạng một danh sách JSON thuần túy, ví dụ: ["Trứng", "Cà chua", "Hành lá"].
    Không thêm bất kỳ định dạng markdown nào khác.
    """
    response = model.generate_content([prompt, image])
    try:
        return json.loads(response.text)
    except:
        return []  # Xử lý lỗi nếu AI không trả về JSON đúng
    
def suggest_recipes(ingredients_list):
    model = genai.GenerativeModel('gemini-2.5-flash')
    ingredients_str = ", ".join(ingredients_list)

    prompt = f"""
    Với các nguyên liệu sau: {ingredients_str}, hãy gợi ý 3 món ăn Việt Nam phù hợp.
    Ưu tiên các món đơn giản, gia đình (như Canh trứng cà chua).
    Trả về kết quả dưới dạng JSON Schema sau:
    [
        {{
            "ten_mon": "Tên món",
            "mo_ta": "Mô tả ngắn",
            "thoi_gian": "Thời gian nấu bằng phút (chỉ ghi số)",
            "do_kho": "Dễ/Trung bình/Khó",
            "nguyen_lieu_can_them": ["Gia vị bổ sung"],
            "huong_dan": ["Bước 1", "Bước 2"]
        }}
    ]
    """

    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)