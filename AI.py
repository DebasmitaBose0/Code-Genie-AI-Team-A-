import streamlit as st
import ollama
from PIL import Image
import pytesseract
import pdfplumber

# ================== CONFIG ==================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
MODEL = "gemma3:1b"

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


# ================== STATE MANAGEMENT ==================
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "full_message" not in st.session_state:
    st.session_state["full_message"] = ""
if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False
if "current_response" not in st.session_state:
    st.session_state["current_response"] = ""


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
                st.session_state["messages"].append({"role": "user", "content": extracted})
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
            if pdf_text.strip():
                st.success("PDF text extraction successful!")
                st.write(pdf_text)
                st.session_state["messages"].append({"role": "user", "content": pdf_text})
            else:
                st.warning("No extractable text found in PDF.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ---------- CHAT SECTION ----------
    st.markdown("<br><div class='deb-section-title'>💬 Chat with DebAI</div>", unsafe_allow_html=True)

    # Show all messages in serial order (user then assistant)
    if len(st.session_state["messages"]) >= 1:
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

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
        stream = ollama.chat(model=MODEL, stream=True, messages=st.session_state["messages"])
        response = ""
        for chunk in stream:
            text = chunk.get("message", {}).get("content", "")
            response += text
            # update session state so reruns can show progress if needed
            st.session_state["current_response"] = response
            yield response
        return response

    # If we just got a prompt, stream assistant response below the conversation
    if st.session_state["is_generating"]:
        partial_response = ""
        with st.chat_message("assistant"):
            placeholder = st.empty()
            # Pass the full messages (including latest user message) to the model
            for partial_response in generate():
                placeholder.markdown(partial_response)
        # generation finished; append final assistant message and clear flag
        st.session_state["full_message"] = partial_response
        st.session_state["messages"].append({"role": "assistant", "content": st.session_state["full_message"]})
        st.session_state["is_generating"] = False
