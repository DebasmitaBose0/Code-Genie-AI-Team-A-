# ✨ Code_Genie
## OCR-Powered Chat Assistant using Streamlit, Tesseract & Python

Code_Genie is a lightweight, modern, and intelligent OCR-based chat assistant that extracts text from PDFs and images and then generates responses using a smart chatbot model. Built for students, developers, and automation enthusiasts who want quick, accurate text extraction and interactive chatting—right inside a beautiful Streamlit UI.

# ⚡ Features
📄 PDF OCR Extraction

Extracts text from scanned or digital PDFs.

# 🖼️ Image OCR Extraction

Reads images and extracts text using Tesseract OCR.

# 🤖 Smart Chat Assistant

Generates intelligent responses based on extracted text or user queries.

# 🎨 Simple & Clean Streamlit UI

Minimal, smooth interface with modern UI placement.

## 🔁 Task-Based Workflow

Organized into tasks (Task 1, Task 2, Task 3) .

# 🛠️ Requirements

1. Python 3.10+

2. Streamlit

3. Tesseract OCR

4. Pillow

5. pdf2image

6. pytesseract

7. tempfile, os

8. pdfplumber

9. Poppler for PDF rendering (Windows)

# 📦 Installation (Windows)
1️⃣ Navigate to project folder
-> cd C:\Users\YourName\Desktop\CodeGenie

2️⃣ Create and activate a virtual environment
-> python -m venv .venv
-> .venv\Scripts\activate

3️⃣ Install dependencies

### If you have requirements.txt:

-> pip install -r requirements.txt

Or manually:

-> pip install streamlit pytesseract pillow pdf2image

4️⃣ Install Tesseract OCR

-> Download Tesseract and install it here:

-> C:\Program Files\Tesseract-OCR\


###  Update this in your Python file:

-> pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

5️⃣ Install Poppler

-> Required for converting PDF pages into images.
-> Install Poppler and add its bin folder to PATH.

▶️ Run the Application

Windows:

-> .venv\Scripts\python.exe -m streamlit run app.py


Streamlit will open automatically at:

-> http://localhost:8501/

# 📘 Project Tasks
## ✅ TASK 1 — PDF & Image Upload UI

1. Design Streamlit layout

2. Add file upload components

3. Handle both PDF and image inputs

4. Show preview of uploaded files

   <img width="1033" height="577" alt="image" src="https://github.com/user-attachments/assets/121d57c9-3ac0-41b0-b29c-22b288da0c57" />


## ✅ TASK 2 — OCR Extraction

For Images:

1. Uses Tesseract OCR

2. Processes .png, .jpg, .jpeg

3. Extracts text efficiently

For PDFs:

1. Converts pages to images via pdf2image

2. Runs OCR on each page

3. Concatenates all extracted text

4. Displays extracted output cleanly

   <img width="1078" height="624" alt="image" src="https://github.com/user-attachments/assets/1fc6de83-0313-4db4-8194-7892271c7b37" />


## ✅ TASK 3 — Chatbot Response Generation

1. Takes OCR text or user-typed query

2. Feeds into chatbot model

3. Generates neat, structured responses

4. Provides final output inside Streamlit

   <img width="1001" height="525" alt="image" src="https://github.com/user-attachments/assets/6c272aaf-53e9-470d-89b8-4fd51975341b" />


# 🎯 Features Added in Your Code

1. Serial message ordering (clean chat sequence)

2. Loading/spinner indicator while generating output

3. Organized Chat UI with separate user and assistant bubbles

4. Clean formatting for OCR output

5. Button to send OCR result directly to Chatbot

6. Works without external APIs (fully local processing)

# 🛠️ Configuration

Tesseract Path:

Update inside your main Python file:

-> pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


PDF to Image Converter:

Set your Poppler path:

-> convert_from_path(pdf_path, poppler_path=r"C:\path\to\poppler\bin")

# 📁 Optional: requirements.txt
1. streamlit
2. pillow
3. pytesseract
4. pdf2image

Project Summary

Code_Genie is designed to provide:

✔ Fast OCR

✔ Clean UI

✔ Intelligent chat responses

✔ Modular and expandable architecture

✔ Perfect for assignments, internships, and real-world projects

# 📜 License (MIT)

MIT License

License
This project is released under the MIT License — see the LICENSE file for details.
