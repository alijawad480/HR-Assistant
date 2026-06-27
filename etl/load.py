from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def get_embeddings():
    """
    Load HuggingFace embedding model.
    all-MiniLM-L6-v2 is small, fast and works well for most use cases.
    It will be downloaded automatically on first run.
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings


def create_vectorstore(chunks, persist_directory="vectorstore/chroma_db"):
    """
    Create embeddings for all chunks and store them in ChromaDB.
    ChromaDB saves to disk so we don't need to recreate every time.
    """
    print("Creating embeddings... this may take a few minutes on first run")

    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )

    print(f"Vectorstore saved to: {persist_directory}")
    return vectorstore


def load_vectorstore(persist_directory="vectorstore/chroma_db"):
    """
    Load existing vectorstore from disk.
    Use this instead of create_vectorstore when documents are already processed.
    """
    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    print("Vectorstore loaded from disk")
    return vectorstore
