import streamlit as st
from PIL import Image
import pytesseract
import re
import google.generativeai as genai
import csv

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
with open(r'api\google_api.txt', 'r') as f:
    gg_api_key = f.readline()

# Tiêu đề trang web
st.title("Food Ingredient Analysis Website")

# Tạo widget để tải file
uploaded_file = st.file_uploader("Choose your menu:", type=["jpg", "jpeg", "png"])

# Process uploaded image 
def tokenizer(text):
    text = re.sub('<[^>]*>', '', text.lower())
    text = re.sub(r"[-.'$—_]", '', text)
    text = re.sub(r'[“”""]', '', text)
    text = re.sub(r"\d+", '', text)
    tokenized = text.split("\n")
    tokenized = [item for item in tokenized if item != '']

    removal_sentence = []
    for idx, sentence in enumerate(tokenized):
        filtered_words = [word for word in sentence.split() if len(word) > 1]
        cleaned_text = " ".join(filtered_words)
        removal_sentence.append(cleaned_text)
    return removal_sentence

genai.configure(api_key = gg_api_key)
model = genai.GenerativeModel('gemini-2.5-pro')

def response_from_ggapi(food, language):
    reply = food
    if st.button("Analysis"):
        status = st.empty()
        status.write("Analyzing image, please wait a minute...")  
        if language == 'vie':
            message = food + " là món ăn được làm từ gì?"
        elif language == 'jpn': 
            message = food + " は何から作られているのですか？"
        elif language == 'eng': 
            message = food + " is a dish made from what?"
        print("Question: ", message)
            
        try:
            response = model.generate_content(message)
            print(response)
            reply += ": " + response.text
        except Exception as e:
            print("Lỗi xảy ra:", e)
        print(1)
        with open("food_detail.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([food,response.text])
 
    return reply



def display(menu): 
    num_choices = len(menu)
    choices = [menu[i] for i in range(int(num_choices))]
    if choices:
        selected = st.radio("Choose the food:", choices)
        st.write("Choosed:", selected)
        if selected:
            option = st.selectbox("Choose language to display:", ["Vietnamese", "Japanese", "English"])
            if option == "Vietnamese":
                response_from_ggapi(selected, 'vie')
            elif option == "Japanese":
                response_from_ggapi(selected, 'jpn')
            elif option == "English":
                response_from_ggapi(selected, 'eng')
        else:
            st.write("Vui lòng chọn một option trước khi nhấn nút.")


def analysis(img, language):
    text = pytesseract.image_to_string(img, lang=language)
    menu = tokenizer(text)
    display(menu)


if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded!", use_container_width =True)
    # Tạo hộp chọn
    option = st.selectbox("Choose language in your image:", ["Vietnamese", "Japanese", "English"])

    # Hiển thị nội dung tương ứng
    if option == "Vietnamese":
        analysis(image, 'vie')
    elif option == "Japanese":
        analysis(image, 'jpn')
    elif option == "English":
        analysis(image, 'eng')
    
    st.write("Would you like to try something else?")

else: 
    st.write("Please upload your image!")


