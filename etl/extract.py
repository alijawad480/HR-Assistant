import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader


def load_documents(folder_path):
    """
    Load all documents from a folder.
    Supports PDF, TXT, and DOCX files.
    """
    documents = []

    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return documents

    files = os.listdir(folder_path)

    if not files:
        print("No files found in the folder")
        return documents

    for filename in files:
        file_path = os.path.join(folder_path, filename)

        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded PDF: {filename} ({len(docs)} pages)")

            elif filename.endswith(".txt"):
                loader = TextLoader(file_path, encoding="utf-8")
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded TXT: {filename}")

            elif filename.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"Loaded DOCX: {filename}")

            else:
                print(f"Skipping unsupported file: {filename}")

        except Exception as e:
            print(f"Error loading {filename}: {e}")

    print(f"\nTotal documents loaded: {len(documents)}")
    return documents
