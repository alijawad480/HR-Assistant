import streamlit as st
import requests
import uuid

# Config
API_URL = "https://onrender.com"

st.set_page_config(
    page_title="HR Document Assistant",
    page_icon="📄",
    layout="wide"
)

# Session State Setup
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "doc_uploaded" not in st.session_state:
    st.session_state.doc_uploaded = False


# Helper Functions
def check_api_status():
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.json()
    except:
        return None


def upload_file(file):
    files = {"file": (file.name, file.getvalue(), file.type)}
    response = requests.post(f"{API_URL}/upload", files=files, timeout=120)
    return response


def ask_question(question, session_id):
    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question, "session_id": session_id},
        timeout=60
    )
    return response


# Page Header
st.title("📄 HR Document Assistant")
st.caption("Upload your HR documents and ask questions in plain English")
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # API Status
    status = check_api_status()
    if status:
        if status["vectorstore_ready"]:
            st.success("✅ Documents Ready")
        else:
            st.warning("⚠️ No documents yet")
    else:
        st.error("❌ API not running\nStart with: uvicorn api.main:app --reload")

    st.divider()

    # File Upload
    st.subheader("📁 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "docx"],
        help="Upload HR policies, SOPs, employee handbooks etc."
    )

    if uploaded_file:
        if st.button("📤 Process Document", use_container_width=True):
            with st.spinner("Processing... please wait"):
                try:
                    response = upload_file(uploaded_file)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ Uploaded successfully!")
                        st.info(f"Chunks created: {data['total_chunks']}")
                        st.session_state.doc_uploaded = True
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Upload failed')}")
                except Exception as e:
                    st.error(f"Cannot connect to API: {str(e)}")

    st.divider()

    # Session Info
    st.subheader("💬 Session")
    st.caption(f"ID: {st.session_state.session_id[:8]}...")

    if st.button("🔄 New Chat Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

    st.divider()
    st.caption("Built with LangChain + FastAPI + ChromaDB")


# Main Chat Area
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Chat")

    # Show all previous messages
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])
            if chat.get("sources"):
                st.caption(f"📎 Source: {', '.join(chat['sources'])}")

    # Chat input
    user_question = st.chat_input("Ask anything about your HR documents...")

    if user_question:
        # Check if vectorstore is ready
        status = check_api_status()
        if not status or not status.get("vectorstore_ready"):
            st.warning("Please upload a document first before asking questions.")
        else:
            # Show user message immediately
            with st.chat_message("user"):
                st.write(user_question)

            st.session_state.chat_history.append({
                "role": "user",
                "content": user_question
            })

            # Get answer from API
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = ask_question(
                            user_question,
                            st.session_state.session_id
                        )

                        if response.status_code == 200:
                            data = response.json()
                            answer = data["answer"]
                            sources = data.get("sources", [])

                            st.write(answer)

                            if sources:
                                st.caption(f"📎 Source: {', '.join(sources)}")

                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": answer,
                                "sources": sources
                            })

                        else:
                            error_msg = response.json().get("detail", "Something went wrong")
                            st.error(f"Error: {error_msg}")

                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to API. Make sure FastAPI is running on port 8000.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

with col2:
    st.subheader("📊 Info")

    st.metric("Messages", len(st.session_state.chat_history))

    if st.session_state.chat_history:
        st.divider()
        st.caption("Recent Questions")
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.caption(f"• {chat['content'][:40]}...")
