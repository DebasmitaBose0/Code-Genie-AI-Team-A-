# -------------------------------------------
# app.py
# ChatGPT-like UI built using Streamlit (UI only)
# -------------------------------------------
# Run these commands in your terminal:
# pip install streamlit
# streamlit run app.py
# -------------------------------------------

import streamlit as st
from datetime import datetime

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Smart Chatbot Interface", layout="wide")

# ---------------------- INITIAL SETUP ----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_name" not in st.session_state:
    st.session_state.chat_name = "New Chat"

# ---------------------- SIDEBAR ----------------------
with st.sidebar:
    st.title("💬 Chat History")

    if not st.session_state.messages:
        st.info("No chats yet. Start a conversation!")
    else:
        for i, msg in enumerate(st.session_state.messages[-5:]):
            st.write(f"{i+1}. {msg['sender'].capitalize()} said: {msg['text'][:30]}...")

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.success("Chat cleared!")

    st.markdown("---")
    st.write("👩‍💻 *Developed using Streamlit UI only*")

    
    # ---------------------- MAIN CONTAINER ----------------------
st.markdown(
    "<h2 style='text-align:center;'>🤖 Smart Chatbot Interface</h2>",
    unsafe_allow_html=True,
)

# Two-column layout
col1, col2 = st.columns([3, 1])

# --- CHAT AREA ---
with col1:
    chat_container = st.container()
    with chat_container:
        if not st.session_state.messages:
            st.markdown("<p style='color:gray;'>No messages yet...</p>", unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                align = "flex-end" if msg["sender"] == "user" else "flex-start"
                bg_color = "#DCF8C6" if msg["sender"] == "user" else "#F1F0F0"
                text_color = "#000"
                bubble = f"""
                <div style='display:flex; justify-content:{align}; margin:5px 0;'>
                    <div style='background:{bg_color}; color:{text_color};
                    padding:10px 14px; border-radius:12px; max-width:70%; 
                    box-shadow:0px 1px 3px rgba(0,0,0,0.1);'>
                        {msg["text"]}
                        <div style='font-size:10px; color:#666; text-align:right; margin-top:4px;'>
                            {msg["time"]}
                        </div>
                    </div>
                </div>
                """
                st.markdown(bubble, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🔍 Ask or Upload:")
# --- Define a callback to clear the input safely ---
    def clear_input():
        st.session_state.user_input = ""

    # --- Input area ---
    user_input = st.text_area(
        "Type your question here...",
        height=70,
        key="user_input",
        placeholder="Enter your message...",
        on_change=None
    )

    col_a, col_b = st.columns([1, 3])
    with col_a:
        send = st.button("📨 Send")

    with col_b:
        uploaded_file = st.file_uploader("Drag and drop file here", type=["jpg", "jpeg", "png", "pdf"])

    if send and user_input.strip() != "":
        st.session_state.messages.append({
            "sender": "user",
            "text": user_input,
            "time": datetime.now().strftime("%I:%M %p")
        })
        # Placeholder bot reply
        st.session_state.messages.append({
            "sender": "bot",
            "text": f"You said: {user_input}",
            "time": datetime.now().strftime("%I:%M %p")
        })

        # ✅ Clear input safely by deleting from session state
        st.session_state.pop("user_input", None)
        st.rerun()

# ---------------------- FOOTER ----------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:gray;'>© Smart Chatbot Interface | UI Version Only</p>",
    unsafe_allow_html=True,
)
