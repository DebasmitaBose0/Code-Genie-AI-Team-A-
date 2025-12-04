import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from PIL import Image
import io
import base64


genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")


MODEL_NAME = "gemini-2.5-pro"


st.set_page_config(page_title="ChatBot", page_icon="💬", layout="wide")


if "chats" not in st.session_state:
    st.session_state.chats = {}

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 0

if "show_uploads" not in st.session_state:
    st.session_state.show_uploads = False

if "pending_image" not in st.session_state:
    st.session_state.pending_image = None

if "menu_for" not in st.session_state:
    st.session_state.menu_for = None

if "rename_mode" not in st.session_state:
    st.session_state.rename_mode = None



def create_new_chat():
    st.session_state.chat_counter += 1
    chat_id = f"chat_{st.session_state.chat_counter}"
    model = genai.GenerativeModel(MODEL_NAME)
    st.session_state.chats[chat_id] = {"messages": [], "chat_session": model.start_chat(history=[]), "title": "New Chat"}
    st.session_state.current_chat_id = chat_id


def switch_chat(chat_id):
    st.session_state.current_chat_id = chat_id


def get_chat_title(chat_data):
    if "title" in chat_data:
        return chat_data["title"]
    messages = chat_data["messages"]
    for msg in messages:
        if msg["role"] == "user":
            for part in msg["parts"]:
                if "text" in part:
                    return " ".join(part["text"].split()[:4])
    return "New Chat"



if st.sidebar.button("🆕 New Chat", use_container_width=True):
    create_new_chat()

st.sidebar.markdown("---")

for chat_id, chat_data in st.session_state.chats.items():
    title = get_chat_title(chat_data)
    col1, col2 = st.sidebar.columns([0.85, 0.15])
    with col1:
        if st.button(title, use_container_width=True, key=f"chat_{chat_id}"):
            switch_chat(chat_id)
    with col2:
        with st.popover("⋮"):
            if st.button("Rename Chat", key=f"rename_{chat_id}"):
                st.session_state.rename_mode = chat_id
                st.rerun()
            if st.button("Delete Chat", key=f"delete_{chat_id}"):
                del st.session_state.chats[chat_id]
                if st.session_state.current_chat_id == chat_id:
                    remaining = list(st.session_state.chats.keys())
                    if remaining:
                        st.session_state.current_chat_id = remaining[0]
                    else:
                        create_new_chat()
                st.rerun()

if st.session_state.rename_mode:
    chat_id = st.session_state.rename_mode
    title = get_chat_title(st.session_state.chats[chat_id])
    st.sidebar.text_input("Rename Chat", value=title, key="rename_input")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Save Rename", key="save_rename"):
            new_title = st.session_state.rename_input
            st.session_state.chats[chat_id]["title"] = new_title
            st.session_state.rename_mode = None
            st.rerun()
    with col2:
        if st.button("Cancel", key="cancel_rename"):
            st.session_state.rename_mode = None
            st.rerun()

if st.session_state.current_chat_id is None:
    create_new_chat()

current_chat = st.session_state.chats[st.session_state.current_chat_id]
messages = current_chat["messages"]
chat_session = current_chat["chat_session"]

st.title("💬 Chatbot")

for message in messages:
    with st.chat_message(message["role"]):
        for part in message["parts"]:
            if "text" in part:
                st.write(part["text"])
            if "image" in part:
                img_data = base64.b64decode(part["image"])
                st.image(img_data)



col1, col2 = st.columns([0.1, 0.9])
with col1:
    if st.button("➕"):
        st.session_state.show_uploads = not st.session_state.show_uploads

with col2:
    user_input = st.chat_input("Type your message...")



if st.session_state.show_uploads:
    st.subheader("📎 Upload Options")

    upload_type = st.radio(
        "Choose an option:",
        ["📷 Camera", "🖼 Photos", "📁 Files"],
        horizontal=True
    )

    uploaded_file = None

    if upload_type == "📷 Camera":
        uploaded_file = st.camera_input("Take a photo")

    elif upload_type == "🖼 Photos":
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    elif upload_type == "📁 Files":
        uploaded_file = st.file_uploader(
            "Upload a file",
            type=["jpg", "jpeg", "png", "pdf", "txt", "docx", "xlsx"]
        )

    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")

        
        if uploaded_file.type in ["image/jpeg", "image/png", "image/jpg"]:
            img = Image.open(io.BytesIO(uploaded_file.read()))
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode()

            st.session_state.pending_image = {"name": uploaded_file.name, "base64": img_base64, "pil": img}
            st.info("Image uploaded. Type your question about it.")
        else:
            st.warning("Only image files are supported for now.")



if user_input:
    user_parts = [{"text": user_input}]
    if st.session_state.pending_image:
        user_parts.append({"image": st.session_state.pending_image["base64"]})
        st.session_state.pending_image = None  # Clear after use

    messages.append({"role": "user", "parts": user_parts})
    with st.chat_message("user"):
        st.write(user_input)
        for part in user_parts:
            if "image" in part:
                img_data = base64.b64decode(part["image"])
                st.image(img_data)

    # Send to chat session
    if any("image" in part for part in user_parts):
        img_part = next(part for part in user_parts if "image" in part)
        img_pil = Image.open(io.BytesIO(base64.b64decode(img_part["image"])))
        response = chat_session.send_message([user_input, img_pil])
        st.session_state.show_uploads = False  # Hide upload section after using image
    else:
        response = chat_session.send_message(user_input)

    bot_reply = response.text
    bot_parts = [{"text": bot_reply}]
    messages.append({"role": "assistant", "parts": bot_parts})

    with st.chat_message("assistant"):
        st.write(bot_reply)

    if len(messages) == 2 and st.session_state.chats[st.session_state.current_chat_id]["title"] == "New Chat":
        try:
            title_prompt = f"Generate a short, concise title for this chat based on the user's first message: {messages[0]['parts'][0]['text']}"
            title_model = genai.GenerativeModel(MODEL_NAME)
            title_response = title_model.generate_content(title_prompt)
            new_title = title_response.text.strip()
            st.session_state.chats[st.session_state.current_chat_id]["title"] = new_title
        except:
            pass  

    st.rerun()
