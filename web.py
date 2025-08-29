import streamlit as st
from PIL import Image
import pytesseract
import re
import google.generativeai as genai
import csv

# Set up additional dts
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
with open(r'api\google_api.txt', 'r') as f:
    gg_api_key = f.readline()
file_path = 'food_detail.csv'
with open(file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    food_detail = list(reader)
        
# Set up the title
st.title("Food Ingredient Analysis Website")

# Upload the image
uploaded_file = st.file_uploader("Choose your menu:", type=["jpg", "jpeg", "png"])

# Process uploaded image to text
def clean_text(text):
    pattern = re.compile(
        r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF'  # Hiragana, Katakana, Kanji
        r'a-zA-Z'                                     # English letters and digits
        r'\s]'                                        # Basic punctuation
    )
    return pattern.sub('', text)

def tokenizer_jpn(text):
    tokenized = clean_text(text)
    tokenized = tokenized.split("\n")
    tokenized = [item for item in tokenized if item != ""]
    return tokenized

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

# Initialize model from gg api
genai.configure(api_key = gg_api_key)
model = genai.GenerativeModel('gemini-2.5-pro')


# Make response about food detail from food name with gg api
def response_from_ggapi(food, language1, language):
    reply = food
    input = [language1, food, language]
    print("input: ", input)
    if st.button("Analysis"):
        if language == 'vie':
            message = food + " là món ăn được làm từ gì?"
        elif language == 'jpn': 
            message = food + " は何から作られているのですか？"
        else:
            message = food + " is a dish made from what?" 

        status = st.empty()
        status.write("Analyzing image, please wait a minute...") 
        a = next((detail[3] for detail in food_detail if detail[:3] == input[:3]), [])
        if a:
            status.write(a)
        else: 
            # Ask gg api for response
            try:
                response = model.generate_content(message)
                reply += ": " + response.text
            except Exception as e:
                print("An error is happened:", e)
            # Print and save response
            status.write(reply)
            with open("food_detail.csv", mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([language1, food, language, reply])


# Set up language and select food name
def analysis(img, language):
    text = pytesseract.image_to_string(img, lang=language)
    menu = tokenizer_jpn(text) if language == 'jpn' else tokenizer(text)
    num_choices = len(menu)
    choices = [menu[i] for i in range(int(num_choices))]
    if choices:
        selected = st.radio("Choose a food to find more information:", choices)
        if selected:
            option = st.selectbox("Choose language to display:", ["Vietnamese", "Japanese", "English"])
            if option == "Vietnamese":
                response_from_ggapi(selected, language, 'vie')
            elif option == "Japanese":
                response_from_ggapi(selected, language, 'jpn')
            else:
                response_from_ggapi(selected, language, 'eng')
        else:
            st.write("Please choose a food again.")


# Upload image and process it
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded!", use_container_width =True)
    option = st.selectbox("Choose language in your image:", ["Vietnamese", "Japanese", "English"])
    if option == "Vietnamese":
        analysis(image, 'vie')
    elif option == "Japanese":
        analysis(image, 'jpn')
    else:
        analysis(image, 'eng')
    st.write("Would you like to try something else?")
else: 
    st.write("Please upload your image!")
