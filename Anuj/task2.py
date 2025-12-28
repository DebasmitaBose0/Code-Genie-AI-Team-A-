
import streamlit as st
from google import genai  
from datetime import datetime
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🤖 Gemini AI Code Chatbot", layout="wide")
st.markdown("<h1 style='text-align:center;'>🤖 Gemini AI Code Chatbot</h1>", unsafe_allow_html=True)

# ---------------- API KEY ----------------
client = genai.Client(api_key="API_KEY")   # FIXED

# ---------------- FUNCTION ----------------
def ask_gemini(prompt, model_name="gemini-2.5-flash-lite"):
    """
    Generate Python code from Gemini API using Python SDK
    """
    try:
        prompt_unique = f"{prompt}\n\n# Request timestamp: {time.time()}"

        # NEW WORKING CALL (generate content)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt_unique
        )

        return response.text or "⚠️ No response from Gemini"
    except Exception as e:
        return f"❌ Error: {e}"

# ---------------- CHAT HISTORY ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- UI ----------------
st.markdown("### Enter your code request or upload a file")
user_input = st.text_input("Type your code request here:")

uploaded_file = st.file_uploader("Or browse a file:", type=["txt", "py"])
if uploaded_file is not None:
    file_content = uploaded_file.read().decode("utf-8")
    st.text_area("File Content", file_content, height=200)
    user_input = file_content

submit_button = st.button("Send")
clear_button = st.button("Clear Chat")

# ---------------- HANDLE SUBMIT ----------------
if submit_button and user_input.strip():
    st.session_state.chat_history.append(("🧑 You", user_input.strip()))

    prompt = (
        f"Write a Python program for the following request:\n"
        f"{user_input}\n"
        f"Include comments and example usage."
    )

    with st.spinner("🤖 Generating response..."):
        response = ask_gemini(prompt, model_name="gemini-2.5-flash-lite")

    st.session_state.chat_history.append(("🤖 Bot", response))

# ---------------- HANDLE CLEAR CHAT ----------------
if clear_button:
    st.session_state.chat_history = []

# ---------------- DISPLAY CHAT ----------------
for sender, message in st.session_state.chat_history:
    if sender == "🧑 You":
        st.markdown(
            f"<div style='background-color:#DCF8C6; "
            f"padding:10px; border-radius:10px; margin:5px 0; text-align:right;'>"
            f"<b>{sender}:</b> {message}</div>",
            unsafe_allow_html=True
        )
    else:
        if "```" in message or "def " in message or "class " in message:
            st.code(message, language="python")
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
