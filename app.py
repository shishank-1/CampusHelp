"""
CampusHelp - Phase 5: Streamlit Web Interface
--------------------------------------------------
The only file the end user actually "sees." Handles login, routes to the
Admin view (upload) or User view (chat), and displays answers with sources.

Usage:
    streamlit run app.py
"""

import tempfile
from pathlib import Path

import streamlit as st

from src.auth import authenticate, is_admin
from src.pipeline import ask_question, upload_and_process

# ---------- Page config ----------
st.set_page_config(page_title="CampusHelp", page_icon="🎓", layout="centered")


# ---------- Session state init ----------
def init_session_state():
    defaults = {
        "logged_in": False,
        "username": None,
        "role": None,
        "chat_history": [],  # list of {"question": ..., "answer": ..., "sources": [...]}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ---------- Login screen ----------
def render_login():
    st.title("🎓 CampusHelp")
    st.caption("Ask questions about exam rules, fees, and campus policies.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")

    if submitted:
        result = authenticate(username, password)
        if result["success"]:
            st.session_state.logged_in = True
            st.session_state.username = result["username"]
            st.session_state.role = result["role"]
            st.rerun()
        else:
            st.error(result["message"])


# ---------- Sidebar (shared across both roles) ----------
def render_sidebar():
    with st.sidebar:
        st.write(f"Logged in as **{st.session_state.username}** ({st.session_state.role})")
        if st.button("Log out"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.chat_history = []
            st.rerun()


# ---------- Admin view ----------
def render_admin_upload():
    st.subheader("📤 Upload a new document")
    st.caption("Adds a PDF or DOCX to the knowledge base. No restart needed.")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx"])

    if uploaded_file is not None and st.button("Process document"):
        with st.spinner(f"Processing {uploaded_file.name}..."):
            # Save the uploaded file to a temp path first, since
            # upload_and_process() expects a real file path on disk.
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            result = upload_and_process(tmp_path, uploaded_file.name)

        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])


# ---------- User view: chat ----------
def render_chat():
    st.subheader("💬 Ask a question")

    # Replay chat history
    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            if turn["sources"]:
                st.caption(f"Source: {', '.join(turn['sources'])}")

    question = st.chat_input("Type your question here...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                result = ask_question(question)
            st.write(result["answer"])
            if result["sources"]:
                st.caption(f"Source: {', '.join(result['sources'])}")

        st.session_state.chat_history.append({
            "question": question,
            "answer": result["answer"],
            "sources": result["sources"],
        })


# ---------- Main routing ----------
def main():
    if not st.session_state.logged_in:
        render_login()
        return

    st.title("🎓 CampusHelp")
    render_sidebar()

    if is_admin(st.session_state.role):
        tab_upload, tab_chat = st.tabs(["📤 Upload Documents", "💬 Ask a Question"])
        with tab_upload:
            render_admin_upload()
        with tab_chat:
            render_chat()
    else:
        render_chat()


if __name__ == "__main__":
    main()