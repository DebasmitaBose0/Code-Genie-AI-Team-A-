# 💬 DebAI

<!-- Tech stack badges (styled like buttons) -->
[![Streamlit](https://img.shields.io/badge/Streamlit-%23FF4B4B.svg?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io) [![Python](https://img.shields.io/badge/Python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org) [![Ollama](https://img.shields.io/badge/Ollama-%23000000.svg?style=for-the-badge)](https://ollama.ai) [![Tesseract](https://img.shields.io/badge/Tesseract-%23007ACC.svg?style=for-the-badge)](https://github.com/tesseract-ocr/tesseract) [![Pillow](https://img.shields.io/badge/Pillow-%23DD0031.svg?style=for-the-badge&logo=python&logoColor=white)](https://python-pillow.org) [![pdfplumber](https://img.shields.io/badge/pdfplumber-%23007ACC.svg?style=for-the-badge)](https://github.com/jsvine/pdfplumber)

DebAI is a lightweight, cyberpunk-styled Streamlit chat assistant that extracts text from images and PDFs (OCR) and chats using an Ollama-backed model. Built for fast testing and local experimentation. ✨

---

## ✨ Features
- 🖼 Image OCR (Tesseract via `pytesseract`)
- 📄 PDF text extraction (`pdfplumber`)
- 🧠 Streaming chat with an Ollama model
- 🎨 Cyberpunk-themed Streamlit UI

---

## ⚙️ Requirements
- Python 3.10+ (tested with Python 3.12)
- Tesseract OCR installed and accessible (Windows default path is used in `AI.py`)
- (Optional) Ollama running locally if you want local model inference

---

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

---

## ▶️ Run the app
From the project root (with virtualenv active):

```bash
# Unix / macOS
streamlit run AI.py

# Windows (venv python)
.venv\Scripts\python.exe -m streamlit run AI.py
```

Open the URL printed by Streamlit (usually `http://localhost:8501` or `http://localhost:8502`). 🔗

---

## 💡 UI & Chat Order Notes
- Messages are displayed in strict serial order (oldest → newest).
- The input box appears below the conversation; when you submit a message it shows immediately, then the assistant streams its reply below it.
- If you see out-of-order messages, restart the app and ensure only one server instance is running.

### New behaviors added in code
- 🔁 Serial chat order: messages are appended and displayed in strict chronological order (user → assistant). The chat input is placed below the conversation so new messages appear at the bottom.
- 🔔 Generating badge: while the model streams a response, a small "Generating…" badge is shown near the conversation to indicate progress.
- 🔀 Auto-send OCR toggle: there is a new sidebar checkbox `Auto-send OCR to model` (default: enabled). When enabled, OCR results from images or PDFs are automatically sent to the model. When disabled, OCR text is appended to the chat and a manual "Send OCR" button appears.
- 🧾 Improved PDF OCR: for pages where `pdfplumber` can't extract text (scanned/image PDFs), the app falls back to running Tesseract OCR on the page image to capture embedded text.
- ⌨️ Hotkey / quick send: a "Send last OCR (Alt+S)" control is available; pressing Alt+S (or clicking the link) will send the most recent OCR result to the model. This uses `st.query_params` and `st.set_query_params()` internally.
- 🔒 Safe streaming & append: assistant streaming output is shown in a single assistant bubble and appended to the message history only once when generation finishes.

---

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

---

## 🔧 Troubleshooting
- Blank Streamlit page: ensure Streamlit is installed and the server prints the local URL. Try a hard refresh.
- OCR returns empty text: confirm Tesseract is installed and `tesseract_cmd` is correct.
- Ollama chat fails: verify Ollama is running and reachable.

---

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

---
Made with ❤️ and neon vibes ✨

## 📜 License
This project is released under the MIT License — see the `LICENSE` file for details.
