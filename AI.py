import streamlit as st
try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    # Ollama may not be available in hosted environments (Streamlit Cloud)
    ollama = None
    OLLAMA_AVAILABLE = False
import os
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except Exception:
    genai = None
    GEMINI_AVAILABLE = False
from PIL import Image
import pytesseract
import pdfplumber

# ================== CONFIG ==================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
MODEL = "gemma3:1b"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

st.set_page_config(
    page_title="DebAI",
    page_icon="💬",
    layout="wide"
)

# ================== CYBERPUNK CSS ==================
cyberpunk_css = """
<style>
.stApp {
    background: radial-gradient(circle at top, #3b0764 0, #020617 45%, #000000 100%);
    color: #e5e7eb;
    font-family: 'Segoe UI', sans-serif;
}

.block-container {
    padding-top: 2rem !important;
}

.debai-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(120deg, #f97316, #e11d48, #a855f7);
    -webkit-background-clip: text;
    color: transparent;
    margin-bottom: 1.8rem;
}

.debai-subtitle {
    margin-top: -1rem;
    font-size: 1rem;
    color: #e5e7ebcc;
    margin-bottom: 2rem;
}

.stTabs {
    margin-top: 1.4rem;
}

.deb-card {
    background: linear-gradient(145deg, rgba(15,23,42,0.92), rgba(67,22,138,0.58));
    border-radius: 18px;
    padding: 1.2rem;
    border: 1px solid rgba(168,85,247,0.38);
    box-shadow: 0 16px 38px rgba(0,0,0,0.6);
    margin-bottom: 1.4rem;
}

.stChatMessage {
    border-radius: 14px !important;
    padding: 0.8rem !important;
}

.stChatMessage[data-testid="stChatMessage-user"] {
    background: rgba(239,68,68,0.15);
    border-left: 3px solid rgba(239,68,68,0.6);
}

.stChatMessage[data-testid="stChatMessage-assistant"] {
    background: rgba(129,140,248,0.20);
    border-left: 3px solid rgba(129,140,248,0.6);
}

</style>
"""
st.markdown(cyberpunk_css, unsafe_allow_html=True)

# ================== SIDEBAR ==================
with st.sidebar:
    st.markdown("### ⚙️ DebAI Control Panel")
    st.markdown("---")
    st.markdown("**Model in use:**")
    st.markdown(f"`{MODEL}`")
    st.markdown("**Capabilities:**")
    st.markdown("- 🖼 Image OCR\n- 📄 PDF OCR\n- 💬 Intelligent Chat")
    st.markdown("---")
    # Toggle: auto-send OCR outputs to the model
    auto_send_ocr = st.checkbox("Auto-send OCR to model", value=True, help="When enabled, OCR text (image/PDF) is sent to the model automatically. When disabled, OCR text is only appended to chat and you can send it manually.")
    st.session_state.setdefault("auto_send_ocr", auto_send_ocr)
    if not OLLAMA_AVAILABLE:
        st.warning("Ollama client not available in this environment — model responses will be disabled. You can still use OCR features.")


# ================== STATE MANAGEMENT ==================
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "full_message" not in st.session_state:
    st.session_state["full_message"] = ""
if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False
if "current_response" not in st.session_state:
    st.session_state["current_response"] = ""
if "last_ocr" not in st.session_state:
    st.session_state["last_ocr"] = ""


# ================== HEADER ==================
st.markdown(
    """
    <div class="debai-title">💬 DebAI — My Cyberpunk Chat Assistant</div>
    <div class="debai-subtitle">Decode images, read PDFs, and think with electric clarity.</div>
    """,
    unsafe_allow_html=True,
)


# ================== OCR + CHAT WRAPPER ==================
main_container = st.container()

with main_container:

    # ---------- OCR TABS ----------
    tab_img, tab_pdf = st.tabs(["🖼 Image OCR", "📄 PDF OCR"])

    with tab_img:
        st.markdown('<div class="deb-card">', unsafe_allow_html=True)
        st.write("Upload an image to extract text and add it to chat context.")
        img = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        if img:
            image = Image.open(img)
            st.image(image, use_container_width=True)
            extracted = pytesseract.image_to_string(image).strip()
            if extracted:
                st.success("Image OCR successful!")
                st.write(extracted)
                # append extracted text as user message
                st.session_state["messages"].append({"role": "user", "content": extracted})
                # save last OCR for manual hotkey send
                st.session_state["last_ocr"] = extracted
                # decide whether to auto-send to model or offer manual send
                if st.session_state.get("auto_send_ocr", True):
                    st.session_state["full_message"] = ""
                    st.session_state["is_generating"] = True
                    st.session_state["current_response"] = ""
                else:
                    if st.button("Send image OCR to model", key="send_img_ocr"):
                        st.session_state["full_message"] = ""
                        st.session_state["is_generating"] = True
                        st.session_state["current_response"] = ""
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_pdf:
        st.markdown('<div class="deb-card">', unsafe_allow_html=True)
        st.write("Upload a PDF and DebAI will read all pages.")
        pdf = st.file_uploader("Upload PDF", type=["pdf"])
        if pdf:
            pdf_text = ""
            with pdfplumber.open(pdf) as pdf_file:
                for page in pdf_file.pages:
                    text = page.extract_text()
                    if text:
                        pdf_text += text + "\n"
                    else:
                        # If no text found, try OCR on the page image to capture embedded text
                        try:
                            page_image = page.to_image(resolution=300)
                            pil_img = page_image.original
                            ocr_text = pytesseract.image_to_string(pil_img).strip()
                            if ocr_text:
                                pdf_text += ocr_text + "\n"
                        except Exception:
                            # fallback: ignore page if OCR fails
                            pass
            if pdf_text.strip():
                st.success("PDF text extraction successful!")
                st.write(pdf_text)
                # append extracted text as user message
                st.session_state["messages"].append({"role": "user", "content": pdf_text})
                # save last OCR for manual hotkey send
                st.session_state["last_ocr"] = pdf_text
                # decide whether to auto-send to model or offer manual send
                if st.session_state.get("auto_send_ocr", True):
                    st.session_state["full_message"] = ""
                    st.session_state["is_generating"] = True
                    st.session_state["current_response"] = ""
                else:
                    if st.button("Send PDF OCR to model", key="send_pdf_ocr"):
                        st.session_state["full_message"] = ""
                        st.session_state["is_generating"] = True
                        st.session_state["current_response"] = ""
            else:
                st.warning("No extractable text found in PDF.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- CHAT SECTION ----------
    st.markdown("<br><div class='deb-section-title'>💬 Chat with DebAI</div>", unsafe_allow_html=True)

    # placeholder for a small "Generating..." badge while model streams
    gen_badge = st.empty()

    # Show all messages in serial order (user then assistant)
    if len(st.session_state["messages"]) >= 1:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Hotkey link: clicking (or pressing Alt+S) will add ?send_last_ocr=1 to URL
    # Streamlit will detect and trigger sending the last OCR result.
    st.markdown(
        "<div style='margin-top:8px'><a href='?send_last_ocr=1' accesskey='s' title='Alt+S (or Option+S on mac) - Send last OCR to model' style='text-decoration:none;padding:6px 10px;border-radius:8px;background:#7c3aed;color:white;font-weight:600'>Send last OCR (Alt+S)</a></div>",
        unsafe_allow_html=True,
    )

    # If the query param is present, trigger generation for the last OCR result
    params = st.query_params
    if "send_last_ocr" in params:
        # Only trigger if we have a saved OCR result
        if st.session_state.get("last_ocr"):
            # Ensure the last OCR is present in messages (it usually is)
            # and trigger generation
            st.session_state["is_generating"] = True
            st.session_state["current_response"] = ""
        # Clear the query params to avoid re-triggering on rerun
        st.set_query_params()

    # Place the chat input below the conversation so user input appears last
    prompt = st.chat_input("Type your message here...")
    if prompt:
        # Append user message to history and display it immediately
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state["full_message"] = ""
        st.session_state["is_generating"] = True
        st.session_state["current_response"] = ""

    def generate():
            # Prefer Ollama when available (local usage)
            if OLLAMA_AVAILABLE and ollama is not None:
                stream = ollama.chat(model=MODEL, stream=True, messages=st.session_state["messages"])
                response = ""
                for chunk in stream:
                    text = chunk.get("message", {}).get("content", "")
                    response += text
                    # update session state so reruns can show progress if needed
                    st.session_state["current_response"] = response
                    yield response
                return response

            # Fallback to Gemini if available and configured
            if GEMINI_AVAILABLE and genai is not None:
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    msg = (
                        "Assistant unavailable: Gemini API key not set (GEMINI_API_KEY).\n\n"
                        "Set the environment variable to enable cloud-model fallback."
                    )
                    st.session_state["current_response"] = msg
                    yield msg
                    return msg

                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(GEMINI_MODEL)
                    
                    # Convert messages to Gemini format
                    gemini_history = []
                    for m in st.session_state["messages"][:-1]: # Exclude last message which is the prompt
                        role = "user" if m["role"] == "user" else "model"
                        gemini_history.append({"role": role, "parts": [m["content"]]})
                    
                    chat = model.start_chat(history=gemini_history)
                    response_stream = chat.send_message(st.session_state["messages"][-1]["content"], stream=True)
                    
                    response = ""
                    for chunk in response_stream:
                        text = chunk.text
                        response += text
                        st.session_state["current_response"] = response
                        yield response
                    return response
                except Exception as e:
                    msg = f"Gemini streaming failed: {e}"
                    st.session_state["current_response"] = msg
                    yield msg
                    return msg

            # If neither Ollama nor Gemini is available, show a helpful message
            msg = (
                "Assistant unavailable: no supported model client found (ollama or google-generativeai).\n\n"
                "Use Ollama locally or set GEMINI_API_KEY for cloud-model fallback."
            )
            st.session_state["current_response"] = msg
            yield msg
            return msg

    # If we just got a prompt, stream assistant response below the conversation
    if st.session_state["is_generating"]:
        partial_response = ""
        # show generating badge while streaming
        gen_badge.markdown(
            "<div style='display:inline-block;padding:6px 10px;border-radius:12px;background:#6b21a8;color:#fff;font-weight:600'>Generating…</div>",
            unsafe_allow_html=True,
        )
        with st.chat_message("assistant"):
            placeholder = st.empty()
            # Pass the full messages (including latest user message) to the model
            for partial_response in generate():
                placeholder.markdown(partial_response)
        # clear the badge after generation finishes
        gen_badge.empty()
        # generation finished; append final assistant message and clear flag
        st.session_state["full_message"] = partial_response
        st.session_state["messages"].append({"role": "assistant", "content": st.session_state["full_message"]})
        st.session_state["is_generating"] = False
