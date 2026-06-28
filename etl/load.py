from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


def get_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return embeddings


def create_vectorstore(chunks, persist_directory="vectorstore/chroma_db"):

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
    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    print("Vectorstore loaded from disk")
    return vectorstore
