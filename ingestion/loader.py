import os
from pathlib import Path
import PyPDF2
import docx
import pandas as pd

def load_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def load_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def load_csv(file_path: str) -> str:
    df = pd.read_csv(file_path)
    # Convert rows to a string representation
    return df.to_string(index=False)

def load_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def load_document(file_path: str) -> str:
    """Loads a document and returns its text content based on file extension."""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    elif ext == ".csv":
        return load_csv(file_path)
    elif ext in [".txt", ".md"]:
        return load_text(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def load_directory(directory_path: str) -> dict[str, str]:
    """Loads all supported documents from a directory."""
    documents = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                text = load_document(file_path)
                documents[file_path] = text
            except ValueError as e:
                print(f"Skipping {file_path}: {e}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    return documents
