import streamlit as st
from app import process_message
from memory_store import load_memory
from rag_pipeline.embeddings import get_embedding_model

USER_ID = "streamlit_user"

# ✅ Load models only once
@st.cache_resource
def load_models():
    print("Loading embedding model...")
    get_embedding_model()
    print("Model loaded.")
    return True

load_models()

st.title("📩 Instagram Sales Agent")

session = load_memory(USER_ID)

# Display chat history
if "chat_ui" not in st.session_state:
    st.session_state.chat_ui = []

for msg in st.session_state.chat_ui:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🔥 If order template is active → multi-line input
if session["order"]["state"] in ["awaiting_template"]:

    order_input = st.text_area("Fill Order Details Below:", height=250)

    if st.button("Submit Order"):
        if order_input:
            st.session_state.chat_ui.append(
                {"role": "user", "content": order_input}
            )

            response = process_message(USER_ID, order_input)

            st.session_state.chat_ui.append(
                {"role": "assistant", "content": response}
            )

            st.rerun()

# Normal chat mode
else:
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.chat_ui.append(
            {"role": "user", "content": user_input}
        )

        response = process_message(USER_ID, user_input)

        st.session_state.chat_ui.append(
            {"role": "assistant", "content": response}
        )

        st.rerun()