import google.generativeai as genai
import streamlit as st
from PIL import Image
from ai_engine import identify_ingredients, suggest_recipes

# Cấu hình trang
st.set_page_config(page_title="Smart Fridge Chef", layout="wide")
noIngredientsFound = False

# Khởi tạo Session State
if 'ingredients' not in st.session_state:
    st.session_state['ingredients'] = []
if 'recipes' not in st.session_state:
    st.session_state['recipes'] = None

st.title("🍳 Chef AI - Trợ Lý Bếp Thông Minh")

# Cột trái: Upload ảnh
col1, col2 = st.columns(2)

with col1:
    st.subheader("Chọn ảnh chứa nguyên liệu")
    # Cho phép chọn camera hoặc upload file
    tab_cam, tab_upload = st.tabs(["Camera", "Tải lên"])
    image_input = None
    with tab_cam:
        cam_img = st.camera_input("Chụp ảnh")
        if cam_img: image_input = cam_img
    with tab_upload:
        up_img = st.file_uploader("Chọn ảnh từ máy", type=['jpg', 'png', 'jpeg'])
        if up_img: image_input = up_img

    if image_input:
        # Hiển thị ảnh và nút phân tích
        img = Image.open(image_input)
        st.image(img, caption="Hãy đảm bảo rằng ảnh có rõ hình dạng nguyên liệu để đạt kết quả chính xác nhất", use_column_width=True)
        if st.button("🔍 Phân tích nguyên liệu", type="primary"):
            with st.spinner("Chef AI đang nhận diện nguyên liệu..."):
                detected = identify_ingredients(img)
                if not detected  == ["Empty"]:
                    st.session_state['ingredients'] = detected
                    st.success("Đã nhận diện nguyên liệu xong! Hãy về đầu trang để xem kết quả nếu bạn đang dùng máy tính.")
                else:
                    noIngredientsFound = True
                    st.error("Không nhận diện được nguyên liệu. Hãy thử đổi góc chụp hay chọn ảnh khác.")

# Cột phải: Kết quả và Công thức
with col2:
    if noIngredientsFound == False:
        if st.session_state['ingredients']:
            st.subheader("Xác nhận nguyên liệu")
            # Cho phép người dùng chỉnh sửa danh sách (Human-in-the-loop)
            final_ingredients = st.multiselect(
                "Đây là những nguyên liệu mà tôi thấy được. Bạn có thể chỉnh sửa lại danh sách nếu cần.",
                options=st.session_state['ingredients'],  # Gợi ý thêm
                default=st.session_state['ingredients']
            )
            if st.button("👨‍🍳 Gợi ý món ăn ngay!"):
                with st.spinner("Chef AI đang suy nghĩ công thức..."):
                    recipes = suggest_recipes(final_ingredients)
                    st.session_state['recipes'] = recipes

    # Hiển thị danh sách món ăn
    if st.session_state['recipes']:
        st.subheader("Thực đơn đề xuất cho bạn")
        for recipe in st.session_state['recipes']:
            with st.expander(f"🍲 {recipe['ten_mon']} ({recipe['thoi_gian']} phút)"):
                st.markdown(f"*{recipe['mo_ta']}*")
                st.write(f"**Độ khó:** {recipe['do_kho']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Nguyên liệu cần:")
                    for item in final_ingredients:
                        st.markdown(f"- ✅ {item}")
                    for item in recipe['nguyen_lieu_can_them']:
                        st.markdown(f"- 🛒 {item} (Bổ sung)")
                with c2:
                    st.markdown("### Cách làm:")
                    for idx, step in enumerate(recipe['huong_dan']):
                        st.markdown(f"**B{idx+1}:** {step}")
                        
st.divider()
st.subheader("💬 Hỏi đáp với Chef AI")

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhận input từ người dùng
if prompt := st.chat_input("Thử hỏi thêm về cách nấu..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gọi Gemini với context (thêm logic gọi API)
    with st.chat_message("assistant"):
        model = genai.GenerativeModel('gemini-2.5-flash')
        # Thêm context từ lịch sử chat và công thức hiện tại (nếu có)
        context = "\n".join([msg["content"] for msg in st.session_state.messages]) + "\nCông thức hiện tại: " + str(st.session_state['recipes'])
        response = model.generate_content(f"Hãy trả lời câu hỏi ẩm thực: {prompt}. Nội dung: {context}")
        response_text = response.text
        st.markdown(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})
