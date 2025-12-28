import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import tempfile
import os
from datetime import datetime
from PIL import Image

# ---------------- OCR CONFIG ----------------
# Set your Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\ANKITA UPADHAYAY\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

# Poppler path for pdf2image
POPPLER_PATH = r"C:\Users\ANKITA UPADHAYAY\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="OCR + Chat Assistant", layout="wide")

st.markdown("<h1 style='text-align:center;'>📄 OCR Extractor + 💬 Chat Assistant</h1>", unsafe_allow_html=True)
st.write("---")

# ---------------- SESSION STORAGE ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- PDF OCR SECTION ----------------
st.subheader("📤 Upload PDF for OCR Extraction")

pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if pdf_file:
    with st.spinner("Processing PDF… Please wait."):
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_file.read())
            pdf_path = tmp.name

        pages = convert_from_path(
            pdf_path,
            dpi=200,
            poppler_path=POPPLER_PATH
        )

        extracted_text = ""

        for idx, page in enumerate(pages):
            st.write(f"Processing Page {idx + 1}...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img:
                page.save(img.name, "PNG")
                text = pytesseract.image_to_string(img.name)
                extracted_text += f"\n\n----- Page {idx + 1} -----\n{text}"

        st.success("PDF OCR Completed Successfully!")

        st.subheader("📌 Extracted PDF Text:")
        st.text_area("Result", extracted_text, height=300)

        st.download_button(
            label="⬇ Download PDF OCR Text",
            data=extracted_text,
            file_name="pdf_ocr_output.txt"
        )

        os.remove(pdf_path)

st.write("---")

# ---------------- IMAGE OCR SECTION ----------------
st.subheader("🖼️ Upload Image for OCR Extraction")

image_file = st.file_uploader("Upload an Image", type=["png", "jpg", "jpeg"])

if image_file:
    with st.spinner("Processing Image… Please wait."):
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
            img_tmp.write(image_file.read())
            img_path = img_tmp.name

        extracted_img_text = pytesseract.image_to_string(img_path)

        st.success("Image OCR Completed Successfully!")

        st.subheader("📌 Extracted Image Text:")
        st.text_area("Image OCR Result", extracted_img_text, height=200)

        st.download_button(
            label="⬇ Download Image OCR Text",
            data=extracted_img_text,
            file_name="image_ocr_output.txt"
        )

        os.remove(img_path)

st.write("---")

# ---------------- CHAT SECTION ----------------
st.subheader("💬 AI Chat Assistant")

user_input = st.text_input("Type your message…")

if st.button("Send"):
    if user_input:
        st.session_state.chat_history.append(("🧑 You", user_input))

        # Placeholder response
        bot_response = "This is your AI response placeholder. OCR and chat are now fully integrated."
        st.session_state.chat_history.append(("🤖 Bot", bot_response))

# ---------------- CLEAR CHAT ----------------
if st.button("Clear Chat History"):
    st.session_state.chat_history = []

# ---------------- DISPLAY CHAT ----------------
for sender, message in st.session_state.chat_history:
    if sender == "🧑 You":
        st.markdown(
            f"<div style='background-color:#DCF8C6; padding:10px; "
            f"border-radius:10px; margin:5px 0; text-align:right;'>"
            f"<b>{sender}:</b> {message}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='background-color:#F1F0F0; padding:10px; "
            f"border-radius:10px; margin:5px 0; text-align:left;'>"
            f"<b>{sender}:</b> {message}</div>",
            unsafe_allow_html=True
        )

# ---------------- FOOTER ----------------
st.markdown(
    f"<div style='font-size:10px; color:#666; text-align:right;'>"
    f"Last updated: {datetime.now().strftime('%I:%M %p')}</div>",
    unsafe_allow_html=True
)
