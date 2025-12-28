import streamlit as st
from fpdf import FPDF
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

def create_pdf(messages):
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 15)
            self.cell(0, 10, 'DebAI Session Report', 0, 1, 'C')
            self.ln(10)
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for msg in messages:
        if msg["role"] == "system":
            continue
        role = msg["role"].upper()
        content = msg["content"]
        # Simple sanitization for latin-1
        content = content.encode('latin-1', 'replace').decode('latin-1')
        
        if role == "USER":
            pdf.set_text_color(59, 130, 246) # Blue
        else:
            pdf.set_text_color(100, 100, 100) # Gray
            
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, txt=f"{role}:", ln=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=content)
        pdf.ln(5)
        
    return pdf.output(dest='S').encode('latin-1')

# Load favicon if available
favicon = "💬"
if os.path.exists("pic.png"):
    try:
        favicon = Image.open("pic.png")
    except Exception:
        pass

st.set_page_config(
    page_title="DebAI",
    page_icon=favicon,
    layout="wide"
)

# ================== THEME MANAGEMENT ==================
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    if st.session_state.theme == "dark":
        st.session_state.theme = "light"
    else:
        st.session_state.theme = "dark"

# Define theme colors
if st.session_state.theme == "dark":
    # 🌑 DARK MODE — “FOCUSED · FUTURISTIC · CINEMATIC”
    dark_bg_image = """
        radial-gradient(circle at 15% 50%, rgba(79, 70, 229, 0.15), transparent 40%),
        radial-gradient(circle at 85% 30%, rgba(59, 130, 246, 0.15), transparent 40%),
        linear-gradient(180deg, #020617 0%, #0f172a 50%, #1e293b 100%)
    """
    
    css_vars = f"""
    --bg-color: #020617;
    --card-bg: rgba(255, 255, 255, 0.08);
    --chat-bg: rgba(255, 255, 255, 0.08);
    --chat-user-bg: rgba(59, 130, 246, 0.15);
    --chat-assistant-bg: rgba(255, 255, 255, 0.05);
    --accent: #60a5fa;
    --accent-glow: rgba(96, 165, 250, 0.4);
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border-color: rgba(255, 255, 255, 0.1);
    --sidebar-bg: #020617;
    --app-bg: {dark_bg_image};
    --glass-blur: 25px;
    --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    --logo-bg: rgba(59, 130, 246, 0.15);
    --logo-border: rgba(59, 130, 246, 0.3);
    --bg-anim: orbFloat 40s ease-in-out infinite alternate;
    """
    btn_label = "☀️ Light Mode"
else:
    # 🌕 LIGHT MODE — “CLEAN · AIRY · APPLE-LEVEL POLISH”
    light_bg_image = """
        radial-gradient(circle at 0% 0%, rgba(219, 234, 254, 0.6), transparent 50%),
        radial-gradient(circle at 100% 100%, rgba(237, 233, 254, 0.6), transparent 50%),
        linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)
    """

    css_vars = f"""
    --bg-color: #ffffff;
    --card-bg: rgba(255, 255, 255, 0.65);
    --chat-bg: rgba(255, 255, 255, 0.65);
    --chat-user-bg: rgba(59, 130, 246, 0.08);
    --chat-assistant-bg: rgba(255, 255, 255, 0.5);
    --accent: #2563eb;
    --accent-glow: rgba(37, 99, 235, 0.15);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --border-color: rgba(203, 213, 225, 0.6);
    --sidebar-bg: rgba(255, 255, 255, 0.85);
    --app-bg: {light_bg_image};
    --glass-blur: 20px;
    --card-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.08);
    --logo-bg: rgba(37, 99, 235, 0.05);
    --logo-border: rgba(37, 130, 235, 0.1);
    --bg-anim: orbFloat 60s ease-in-out infinite alternate;
    """
    btn_label = "🌙 Dark Mode"

# ================== STYLED UI CSS ==================
cyberpunk_css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

:root {{
    {css_vars}
}}

html, body, .stApp {{
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, Roboto, 'Helvetica Neue', Arial;
    background-color: var(--bg-color);
    color: var(--text-primary);
}}

/* Main Background with Noise */
.stApp {{
    background-color: var(--bg-color);
    background-image: var(--app-bg);
    background-attachment: fixed;
    background-size: 120% 120%;
    animation: var(--bg-anim);
}}

/* Subtle Noise Overlay */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
}}

@keyframes orbFloat {{
    0% {{ background-position: 0% 0%; }}
    100% {{ background-position: 20% 10%; }}
}}

/* Loader Animation */
@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

.loader {{
    border: 3px solid rgba(128, 128, 128, 0.2);
    border-top: 3px solid var(--accent);
    border-radius: 50%;
    width: 24px;
    height: 24px;
    animation: spin 1s linear infinite;
    display: inline-block;
    box-sizing: border-box;
}}

.block-container {{
    padding: 6rem 2rem 4rem 2rem !important;
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}}

/* Text Colors */
h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown, .stText, .stButton, a {{
    color: var(--text-primary) !important;
}}

.debai-subtitle, .stMarkdown p {{
    color: var(--text-secondary) !important;
}}

/* Ultimate Glass Card */
.deb-card {{
    background: var(--card-bg);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--border-color);
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 24px;
    padding: 2rem;
    box-shadow: var(--card-shadow);
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 1;
    transition: background 0.5s ease, backdrop-filter 0.5s ease, box-shadow 0.5s ease, border-color 0.5s ease;
}}

.stTabs {{
    margin-top: 1rem;
}}

/* Header */
.debai-title {{
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, var(--accent) 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    text-shadow: 0 0 30px var(--accent-glow);
    transition: all 0.5s ease;
}}

.debai-subtitle {{
    margin-top: 0;
    font-size: 0.95rem;
    color: var(--text-secondary);
    margin-bottom: 1.25rem;
}}

.debai-header {{
    display:flex;align-items:center;gap:12px;margin-bottom:8px;
}}

.debai-logo {{
    width:44px;height:44px;
    background: var(--logo-bg);
    border: 1px solid var(--logo-border);
    box-shadow: 0 0 20px var(--accent-glow);
    border-radius: 16px;
    padding: 8px;
    display:inline-flex;align-items:center;justify-content:center;
    transition: all 0.5s ease;
}}
.debai-logo svg {{
    width:24px;height:24px;
    fill: var(--accent);
    transition: fill 0.5s ease;
}}

/* Sidebar */
section[data-testid='stSidebar'] {{
    background-color: var(--sidebar-bg);
    border-right: 1px solid var(--border-color);
    transition: background-color 0.5s ease, border-color 0.5s ease;
}}
section[data-testid='stSidebar'] .stMarkdown, 
section[data-testid='stSidebar'] label,
section[data-testid='stSidebar'] .stCheckbox,
section[data-testid='stSidebar'] .css-1l02y0g {{
    color: var(--text-secondary) !important;
}}
section[data-testid='stSidebar'] svg {{
    fill: var(--text-secondary) !important;
}}

/* Expander */
div[data-testid="stExpander"] details summary {{
    color: var(--text-primary) !important;
    background-color: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}}
div[data-testid="stExpander"] details summary:hover {{
    color: var(--accent) !important;
    background-color: rgba(255, 255, 255, 0.1);
}}
div[data-testid="stExpander"] details {{
    border-color: var(--border-color);
}}

/* Chat Bubbles - Ultimate Glass */
.stChatMessage {{
    background: var(--chat-bg);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--border-color);
    border-radius: 20px !important;
    padding: 1.25rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    font-size: 1rem;
    margin-bottom: 16px;
    position: relative;
    z-index: 1;
    transition: background 0.5s ease, border-color 0.5s ease, backdrop-filter 0.5s ease;
}}

.stChatMessage[data-testid="stChatMessage-user"] {{
    background: var(--chat-user-bg);
    border: 1px solid var(--accent);
    color: var(--text-primary);
}}
.stChatMessage[data-testid="stChatMessage-assistant"] {{
    background: var(--chat-assistant-bg);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
}}

/* Buttons & Inputs */
.stButton button, .stDownloadButton button {{
    background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
    color: white !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}}
.stButton button:hover, .stDownloadButton button:hover {{
    box-shadow: 0 0 15px var(--accent-glow);
    transform: translateY(-1px);
    color: white !important;
}}

/* Send OCR Button */
.send-ocr-btn {{
    display: inline-block;
    padding: 8px 16px;
    border-radius: 8px;
    background: rgba(59, 130, 246, 0.15);
    color: var(--accent) !important;
    font-weight: 600;
    text-decoration: none;
    border: 1px solid rgba(59, 130, 246, 0.3);
    transition: all 0.2s;
}}
.send-ocr-btn:hover {{
    background: rgba(59, 130, 246, 0.25);
    box-shadow: 0 0 10px var(--accent-glow);
}}

/* Custom Scrollbar */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: var(--border-color);
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: var(--accent);
}}

/* Text Input & Text Area */
.stTextInput input, .stTextArea textarea {{
    background-color: var(--card-bg) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    padding: 12px !important;
    backdrop-filter: blur(var(--glass-blur));
    transition: all 0.3s ease;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 15px var(--accent-glow) !important;
}}

/* Small responsive tweaks */
@media (max-width: 760px) {{
    .debai-title {{ font-size: 1.6rem; }}
    .block-container {{ padding-left: 1rem !important; padding-right:1rem !important; }}
}}

/* File Uploader Fixes */
[data-testid='stFileUploader'] section {{
    background-color: var(--card-bg) !important;
    border: 1px dashed var(--border-color) !important;
}}
[data-testid='stFileUploader'] section > div {{
    color: var(--text-secondary) !important;
}}
[data-testid='stFileUploader'] section small {{
    color: var(--text-secondary) !important;
}}
[data-testid='stFileUploader'] button {{
    background-color: var(--accent) !important;
    color: white !important;
    border: none !important;
}}
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

    st.markdown("---")
    if len(st.session_state.get("messages", [])) > 0:
        st.markdown("### 📥 Export Chat")
        pdf_data = create_pdf(st.session_state["messages"])
        st.download_button(
            label="Download Report (PDF)",
            data=pdf_data,
            file_name="debai_report.pdf",
            mime="application/pdf"
        )


# ================== STATE MANAGEMENT ==================
system_prompt = (
    "You are a helpful AI assistant named DebAI. "
    "You are trilingual. "
    "RULE: You MUST respond in the same language as the user. "
    "1. User speaks Bengali (or Banglish) -> You speak Bengali (Bangla Script). Example: 'tumi kemon acho' -> 'তুমি কেমন আছো?'. "
    "2. User speaks Hindi (or Hinglish) -> You speak Hindi (Devanagari Script). Example: 'aap kaise hain' -> 'आप कैसे हैं?'. "
    "3. User speaks English -> You speak English. "
    "Do not provide translations or explanations in English if the user speaks Bengali or Hindi."
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
else:
    # Ensure system message is present and up-to-date for existing sessions
    if len(st.session_state["messages"]) > 0 and st.session_state["messages"][0]["role"] == "system":
        st.session_state["messages"][0]["content"] = system_prompt
    else:
        st.session_state["messages"].insert(0, {"role": "system", "content": system_prompt})

if "full_message" not in st.session_state:
    st.session_state["full_message"] = ""
if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False
if "current_response" not in st.session_state:
    st.session_state["current_response"] = ""
if "last_ocr" not in st.session_state:
    st.session_state["last_ocr"] = ""


# ================== HEADER ==================
# Top right toggle
col1, col2 = st.columns([0.85, 0.15])
with col2:
    st.button(btn_label, on_click=toggle_theme, key="theme_toggle")

# Header: show an image logo if available in workspace, otherwise use inline SVG
logo_path = None
if os.path.exists("assets/logo.png"):
    logo_path = "assets/logo.png"
elif os.path.exists("logo.png"):
    logo_path = "logo.png"

if logo_path:
    cols = st.columns([0.12, 0.88])
    with cols[0]:
        st.image(logo_path, width=56)
    with cols[1]:
        st.markdown(
            """
            <div class='debai-title'>DebAI — Intelligent OCR Assistant</div>
            <div class='debai-subtitle'>Extract text from images and PDFs, then chat intelligently.</div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div class="debai-header">
            <div class="debai-logo" aria-hidden="true">
                <!-- Abstract Eye + Chat Bubble Logo -->
                <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#3B82F6;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#8B5CF6;stop-opacity:1" />
                        </linearGradient>
                        <filter id="glow">
                            <feGaussianBlur stdDeviation="1.5" result="coloredBlur"/>
                            <feMerge>
                                <feMergeNode in="coloredBlur"/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                    </defs>
                    <path d="M32 8 C18 8 6 18 6 30 C6 38 10 44 16 48 L14 56 L24 52 C26.5 52.5 29.2 52.8 32 52.8 C46 52.8 58 42.8 58 30.8 C58 18.8 46 8.8 32 8.8 Z M32 44 C23 44 16 37 16 29 C16 21 23 14 32 14 C41 14 48 21 48 29 C48 37 41 44 32 44 Z" fill="none" stroke="url(#grad1)" stroke-width="3" filter="url(#glow)"/>
                    <circle cx="32" cy="29" r="5" fill="url(#grad1)" filter="url(#glow)"/>
                    <path d="M32 22 C35 22 38 24 38 29" fill="none" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round" opacity="0.8"/>
                </svg>
            </div>
            <div>
                <div class="debai-title">DebAI</div>
                <div class="debai-subtitle">Intelligent OCR & Chat Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ================== OCR + CHAT WRAPPER ==================
main_container = st.container()

with main_container:

    # ---------- OCR TABS ----------
    with st.expander("📂 Upload Documents (Image/PDF)", expanded=True):
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
            if msg["role"] == "system":
                continue
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Hotkey link: clicking (or pressing Alt+S) will add ?send_last_ocr=1 to URL
    # Streamlit will detect and trigger sending the last OCR result.
    st.markdown(
        "<div style='margin-top:8px'><a href='?send_last_ocr=1' accesskey='s' title='Alt+S (or Option+S on mac) - Send last OCR to model' class='send-ocr-btn'>Send last OCR (Alt+S)</a></div>",
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
        try:
            st.query_params.clear()
        except:
            pass

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
            # Deterministic Language Detection based on Unicode ranges
            last_user_msg = st.session_state["messages"][-1]["content"]
            
            # Bengali Unicode Block: U+0980 to U+09FF
            has_bengali = any('\u0980' <= char <= '\u09FF' for char in last_user_msg)
            # Devanagari (Hindi) Unicode Block: U+0900 to U+097F
            has_hindi = any('\u0900' <= char <= '\u097F' for char in last_user_msg)
            
            if has_bengali:
                lang_instruction = (
                    "\n\n[SYSTEM INSTRUCTION: The user is writing in Bengali. "
                    "You MUST respond ONLY in Bengali (Bangla script). "
                    "Do not use Hindi or English.]"
                )
            elif has_hindi:
                lang_instruction = (
                    "\n\n[SYSTEM INSTRUCTION: The user is writing in Hindi. "
                    "You MUST respond ONLY in Hindi (Devanagari script). "
                    "Do not use Bengali or English.]"
                )
            else:
                # Latin script: Check for transliterated Hindi or Bengali
                lang_instruction = (
                    "\n\n[SYSTEM INSTRUCTION: The user is writing in Latin script. "
                    "Analyze the text for phonetic Hindi or Bengali. "
                    "1. If it is Hindi (e.g., 'kya haal hai', 'namaste'), respond ONLY in Hindi (Devanagari script). "
                    "2. If it is Bengali (e.g., 'kemon acho', 'ki khobor'), respond ONLY in Bengali (Bangla script). "
                    "3. If it is English, respond in English. "
                    "Respond in the detected language script only.]"
                )

            # Prefer Ollama when available (local usage)
            if OLLAMA_AVAILABLE and ollama is not None:
                # Create a copy of messages to avoid modifying the UI state
                messages_payload = [m.copy() for m in st.session_state["messages"]]
                if messages_payload and messages_payload[-1]["role"] == "user":
                    messages_payload[-1]["content"] += lang_instruction

                stream = ollama.chat(model=MODEL, stream=True, messages=messages_payload)
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
                    
                    # Extract system instruction if present
                    system_instruction = None
                    gemini_history = []
                    for m in st.session_state["messages"][:-1]: # Exclude last message which is the prompt
                        if m["role"] == "system":
                            system_instruction = m["content"]
                            continue
                        role = "user" if m["role"] == "user" else "model"
                        gemini_history.append({"role": role, "parts": [m["content"]]})

                    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_instruction)
                    
                    chat = model.start_chat(history=gemini_history)
                    
                    user_msg = st.session_state["messages"][-1]["content"] + lang_instruction
                    response_stream = chat.send_message(user_msg, stream=True)
                    
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
            """
            <div style="display: flex; align-items: center; gap: 12px; padding: 12px 20px; background: var(--card-bg); border-radius: 16px; border: 1px solid var(--border-color); width: fit-content; backdrop-filter: blur(var(--glass-blur)); box-shadow: var(--card-shadow);">
                <div class="loader"></div>
                <span style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">Thinking...</span>
            </div>
            """,
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
