# HR Document Assistant

An AI-powered chatbot that lets you upload HR documents and ask questions in natural language.
Built with LangChain, FastAPI, ChromaDB, HuggingFace, and Streamlit.

---

## What This Project Does

- Upload PDF, TXT, or DOCX files (HR policies, SOPs, handbooks)
- Ask questions in plain English
- Get accurate answers from your documents
- Remembers conversation history within a session
- Saves all chats to SQLite database

---

## Project Structure

```
hr_document_assistant/
├── etl/
│   ├── extract.py       # Load documents from folder
│   ├── transform.py     # Split documents into chunks
│   └── load.py          # Create embeddings and save to ChromaDB
├── rag/
│   └── chain.py         # RAG chain connecting vectorstore + LLM
├── api/
│   └── main.py          # FastAPI backend with all endpoints
├── frontend/
│   └── app.py           # Streamlit chat interface
├── database/
│   └── db.py            # SQLite for chat history
├── data/
│   └── documents/       # Put your HR documents here
├── vectorstore/         # ChromaDB saves here automatically
├── run_etl.py           # Run ETL pipeline manually
├── requirements.txt
└── .env                 # Your API keys go here
```

---

## Setup Instructions

### Step 1: Create Virtual Environment

```bash
python -m venv venv
```

Activate it:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Note: First time installing sentence-transformers will download the embedding model automatically.

### Step 3: Get Free Groq API Key

1. Go to https://console.groq.com
2. Sign up for free
3. Create an API key
4. Open the `.env` file and replace `your_groq_api_key_here` with your actual key

```
GROQ_API_KEY=gsk_your_actual_key_here
```

### Step 4: Add Your Documents (Optional)

Put any PDF, TXT, or DOCX files in the `data/documents/` folder.
A sample HR policy file is already there for testing.

---

## How to Run

You need to open TWO terminals side by side.

### Terminal 1 - Start FastAPI Backend

```bash
uvicorn api.main:app --reload
```

You will see: `Uvicorn running on http://127.0.0.1:8000`

### Terminal 2 - Start Streamlit Frontend

```bash
streamlit run frontend/app.py
```

Browser will open automatically at http://localhost:8501

---

## How to Use

1. Open browser at http://localhost:8501
2. In the sidebar, upload a document (PDF, TXT, DOCX)
3. Click "Process Document" and wait for it to finish
4. Type your question in the chat box
5. Get answers with source references

---

## API Endpoints (FastAPI)

View all endpoints at: http://localhost:8000/docs

| Method | Endpoint | What it does |
|--------|----------|-------------|
| GET | / | Check if API is running |
| GET | /health | Check API and vectorstore status |
| GET | /new-session | Get a new session ID |
| POST | /upload | Upload a document |
| POST | /ask | Ask a question |
| GET | /history/{session_id} | Get chat history |
| GET | /sessions | Get all sessions |
| DELETE | /session/{session_id} | Clear a session |

---

## Run ETL Manually (Optional)

If you want to process documents without using the API:

```bash
python run_etl.py
```

This will process all files in `data/documents/` folder.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| LangChain | Document loading, text splitting, RAG chain |
| LangGraph | Not used in this project (used in Project 2) |
| HuggingFace | Embedding model (sentence-transformers) |
| ChromaDB | Vector database to store embeddings |
| Groq | Free LLM API (llama3-8b) |
| FastAPI | REST API backend |
| SQLite | Store chat history |
| Streamlit | Chat interface frontend |

---

## Sample Questions to Test

After uploading the sample HR policy file, try these:

- How many days of annual leave do I get?
- What is the notice period for resignation?
- Tell me about the health insurance policy
- What happens if my performance rating is below 2?
- How much training budget do I get per year?
