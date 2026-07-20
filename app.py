import os
import argparse
from ingestion.loader import load_directory, load_document
from ingestion.chunker import RecursiveTextChunker
from retrieval.retriever import Retriever
from generation.llm_client import LLMClient
from config import config

def ingest_data(data_path: str):
    """Orchestrates loading, chunking, and ingesting documents into vector store."""
    print(f"Starting ingestion for path: {data_path}")
    
    # 1. Load documents
    documents = {}
    if os.path.isdir(data_path):
        documents = load_directory(data_path)
    elif os.path.isfile(data_path):
        try:
            text = load_document(data_path)
            documents[data_path] = text
        except Exception as e:
            print(f"Error loading {data_path}: {e}")
    else:
        print(f"Invalid path: {data_path}")
        return

    if not documents:
        print("No documents found to ingest.")
        return

    print(f"Loaded {len(documents)} document(s). Chunking...")
    
    # 2. Chunk text
    chunker = RecursiveTextChunker(chunk_size=config.chunk_size, chunk_overlap=config.chunk_overlap)
    all_chunks = []
    all_metadatas = []
    
    for path, text in documents.items():
        chunks = chunker.split_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({"source": path, "chunk_index": i})
            
    print(f"Generated {len(all_chunks)} chunks in total. Ingesting to Qdrant...")
    
    # 3. Ingest to vector store
    retriever = Retriever()
    retriever.ingest(all_chunks, all_metadatas)
    
    print("Ingestion complete.")

def query_rag(query: str):
    """Orchestrates retrieval and generation for a user query."""
    print(f"\nQuery: {query}")
    
    # 1. Retrieve and Rerank
    retriever = Retriever()
    print("Retrieving context...")
    contexts = retriever.retrieve(query, top_k=10, rerank_top_k=3)
    
    if not contexts:
        print("No relevant context found. Answering based on general knowledge or prompting.")
    else:
        print(f"Retrieved {len(contexts)} highly relevant chunks.")
        
    # 2. Generate
    llm = LLMClient()
    print("Generating response...")
    answer = llm.generate_answer(query, contexts)
    
    print("\n--- Answer ---")
    print(answer)
    print("--------------\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Production RAG Pipeline Orchestrator")
    subparsers = parser.add_subparsers(dest="command")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents into the vector store")
    ingest_parser.add_argument("--path", type=str, default="./data", help="Path to file or directory to ingest")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Ask a question using the RAG pipeline")
    query_parser.add_argument("text", type=str, help="The question to ask")
    
    args = parser.parse_args()
    
    if args.command == "ingest":
        ingest_data(args.path)
    elif args.command == "query":
        query_rag(args.text)
    else:
        parser.print_help()
