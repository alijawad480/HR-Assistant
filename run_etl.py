"""
Run this script to manually process documents in the data/documents folder.
Usage: python run_etl.py

This will:
1. Extract all PDF, TXT, DOCX files from data/documents
2. Split them into chunks
3. Create embeddings and store in ChromaDB
"""

from etl.extract import load_documents
from etl.transform import split_documents
from etl.load import create_vectorstore
from database.db import init_db


def run_etl():
    print("=" * 40)
    print("HR Document Assistant - ETL Pipeline")
    print("=" * 40)

    # Step 1: Initialize database
    print("\nInitializing database...")
    init_db()

    # Step 2: Extract documents
    print("\n--- STEP 1: EXTRACT ---")
    documents = load_documents("data/documents")

    if not documents:
        print("\nNo documents found!")
        print("Please add PDF, TXT, or DOCX files to the 'data/documents' folder")
        return

    # Step 3: Transform (split into chunks)
    print("\n--- STEP 2: TRANSFORM ---")
    chunks = split_documents(documents)

    # Step 4: Load into vector store
    print("\n--- STEP 3: LOAD ---")
    vectorstore = create_vectorstore(chunks, "vectorstore/chroma_db")

    print("\n" + "=" * 40)
    print("ETL Pipeline Completed!")
    print(f"Documents processed : {len(documents)}")
    print(f"Chunks stored       : {len(chunks)}")
    print("You can now run the API and ask questions")
    print("=" * 40)


if __name__ == "__main__":
    run_etl()
