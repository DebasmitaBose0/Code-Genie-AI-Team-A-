# 🚀 DebAI

DebAI is a lightweight, cyberpunk-styled Streamlit chat assistant that extracts text from images and PDFs (OCR) and chats using an Ollama-backed model. Built for fast testing and local experimentation. ✨

## ✨ Features
- 🖼 Image OCR (Tesseract via `pytesseract`)
- 📄 PDF text extraction (`pdfplumber`)
- 🧠 Streaming chat with an Ollama model
- 🎨 Cyberpunk-themed Streamlit UI

## ⚙️ Requirements
- Python 3.10+ (tested with Python 3.12)
- Tesseract OCR installed and accessible (Windows default path is used in `AI.py`)
- (Optional) Ollama running locally if you want local model inference

## 🛠️ Setup (Windows)
1. Open the project directory:

```bash
cd C:\Users\Debasmita\Desktop\AI
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install streamlit ollama pillow pytesseract pdfplumber
```

4. Install Tesseract OCR (Windows):
- Download and install Tesseract (e.g., to `C:\Program Files\Tesseract-OCR`) and ensure the path matches `pytesseract.pytesseract.tesseract_cmd` in `AI.py`.

5. (Optional) Run Ollama and ensure a compatible model is available (change `MODEL` in `AI.py` if needed).

## ▶️ Run the app
From the project root (with virtualenv active):

```bash
# Unix / macOS
streamlit run AI.py

# Windows (venv python)
.venv\Scripts\python.exe -m streamlit run AI.py
```

Open the URL printed by Streamlit (usually `http://localhost:8501` or `http://localhost:8502`). 🔗

## 💡 UI & Chat Order Notes
- Messages are displayed in strict serial order (oldest → newest).
- The input box appears below the conversation; when you submit a message it shows immediately, then the assistant streams its reply below it.
- If you see out-of-order messages, restart the app and ensure only one server instance is running.

## 🛠 Configuration
- Tesseract path in `AI.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Change this path if Tesseract is installed elsewhere.

- Ollama model:

```python
MODEL = "gemma3:1b"
```

Update `MODEL` to a model you have locally (or an available Ollama model).

## 🔧 Troubleshooting
- Blank Streamlit page: ensure Streamlit is installed and the server prints the local URL. Try a hard refresh.
- OCR returns empty text: confirm Tesseract is installed and `tesseract_cmd` is correct.
- Ollama chat fails: verify Ollama is running and reachable.

## 📦 Optional: `requirements.txt`
Create a `requirements.txt` with:

```
streamlit
ollama
pillow
pytesseract
pdfplumber
```

Install with `pip install -r requirements.txt`.

## 📄 License
This repository contains sample code. Add a license if you plan to publish or share broadly.

---
Made with ❤️ and neon vibes ✨
