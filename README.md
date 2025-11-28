# DebAI

DebAI is a lightweight Streamlit-based chat assistant that can extract text from images and PDFs (OCR) and chat using a local model via the `ollama` Python client.

## Features
- Image OCR using `pytesseract` (Tesseract OCR)
- PDF text extraction using `pdfplumber`
- Streaming chat with an Ollama model
- Simple, cyberpunk-themed Streamlit UI

## Requirements
- Python 3.10+ (this project was tested with Python 3.12)
- Tesseract OCR installed and accessible (Windows default path shown in `AI.py`)
- Optional: Ollama (local model host) if you plan to use local models

## Setup (Windows)
1. Clone or open the project directory:

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
pip install streamlit ollama pillow pytesseract pdfplumber
```

4. Install Tesseract OCR (Windows):
- Download and install Tesseract (e.g., to `C:\Program Files\Tesseract-OCR`) and ensure the executable path matches the `pytesseract.pytesseract.tesseract_cmd` in `AI.py`.

5. (Optional) Install and run Ollama if you want to use a local model. Ensure the `ollama` client can reach the Ollama service and that a suitable model is available.

## Run the app
From the project root (with the virtualenv active):

```bash
# Linux / macOS
streamlit run AI.py

# Windows (using venv python executable)
.venv\Scripts\python.exe -m streamlit run AI.py
```

After starting, open the URL printed by Streamlit (usually `http://localhost:8501` or `http://localhost:8502`).

## Notes about the UI and chat order
- The app displays messages in serial order (oldest → newest). The chat input is placed below the conversation. When you submit a message, it is appended and shown immediately; the assistant response streams below it and is appended once complete.
- If you see out-of-order messages, restart the app and ensure only one terminal session runs the server.

## Configuration
- Tesseract path in `AI.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Change this path if Tesseract was installed elsewhere.

- Ollama model name is set in `AI.py` as `MODEL = "gemma3:1b"`. Change it to a model you have available if needed.

## Troubleshooting
- If the Streamlit page is blank: ensure Streamlit is installed, and that the app console shows the local URL. Try a hard refresh in the browser.
- If OCR returns empty text: verify Tesseract is installed and the `tesseract_cmd` path is correct.
- If the Ollama chat fails: confirm the Ollama service is running and reachable from Python.

## License
This repository contains sample code — add your preferred license if you plan to share it.
