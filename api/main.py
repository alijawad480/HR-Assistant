import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from etl.extract import load_documents
from etl.transform import split_documents
from etl.load import create_vectorstore, load_vectorstore
from rag.chain import create_rag_chain
from database.db import init_db, save_message, get_chat_history, get_all_sessions

# --- App Setup ---
app = FastAPI(
    title="HR Document Assistant API",
    description="Upload HR documents and ask questions using RAG"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Folders ---
UPLOAD_FOLDER = "data/documents"
VECTORSTORE_PATH = "vectorstore/chroma_db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("vectorstore", exist_ok=True)

# --- Global State ---
vectorstore = None
rag_chain = None   # Single chain shared across sessions (history is per session inside chain)

# Initialize DB on startup
init_db()

# Load existing vectorstore from disk if available
if os.path.exists(VECTORSTORE_PATH):
    try:
        vectorstore = load_vectorstore(VECTORSTORE_PATH)
        rag_chain = create_rag_chain(vectorstore)
        print("Existing vectorstore loaded on startup")
    except Exception as e:
        print(f"Could not load vectorstore: {e}")


# --- Request Models ---
class QuestionRequest(BaseModel):
    question: str
    session_id: str


# --- Endpoints ---

@app.get("/")
def home():
    return {"message": "HR Document Assistant API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "vectorstore_ready": vectorstore is not None,
    }


@app.get("/new-session")
def new_session():
    """Generate a new unique session ID for a user"""
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document and run the ETL pipeline.
    Accepted formats: PDF, TXT, DOCX
    """
    global vectorstore, rag_chain

    # Check file type
    allowed_extensions = [".pdf", ".txt", ".docx"]
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="File type not supported. Please upload PDF, TXT, or DOCX files only."
        )

    # Save uploaded file to disk
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    print(f"File saved: {file.filename}")

    # Run ETL Pipeline
    try:
        documents = load_documents(UPLOAD_FOLDER)
        chunks = split_documents(documents)
        vectorstore = create_vectorstore(chunks, VECTORSTORE_PATH)
        rag_chain = create_rag_chain(vectorstore)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    return {
        "message": f"File '{file.filename}' uploaded and processed successfully",
        "total_chunks": len(chunks)
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):
    """
    Ask a question about the uploaded documents.
    session_id is used to keep separate conversation history per user.
    """
    global vectorstore, rag_chain

    if vectorstore is None or rag_chain is None:
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded yet. Please upload a document first using /upload"
        )

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # Invoke the chain with session id for memory
        response = rag_chain.invoke(
            {"input": request.question},
            config={"configurable": {"session_id": request.session_id}}
        )

        answer = response["answer"]

        # Extract source document names
        sources = []
        for doc in response.get("context", []):
            source = doc.metadata.get("source", "")
            if source:
                sources.append(os.path.basename(source))

        sources = list(set(sources))

        # Save to SQLite
        save_message(request.session_id, "user", request.question)
        save_message(request.session_id, "assistant", answer)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting answer: {str(e)}")

    return {
        "answer": answer,
        "sources": sources,
        "session_id": request.session_id
    }


@app.get("/history/{session_id}")
def get_history(session_id: str):
    """Get full chat history for a specific session"""
    history = get_chat_history(session_id)
    return {
        "session_id": session_id,
        "total_messages": len(history),
        "history": history
    }


@app.get("/sessions")
def get_sessions():
    """Get all sessions"""
    sessions = get_all_sessions()
    return {
        "total_sessions": len(sessions),
        "sessions": sessions
    }


@app.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Clear a session"""
    return {"message": f"Session {session_id} cleared"}
