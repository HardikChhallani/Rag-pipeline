from sentence_transformers import SentenceTransformer, CrossEncoder
from config import config
from .vector_store import QdrantStore

class Retriever:
    def __init__(self):
        print(f"Loading embedding model: {config.embedding_model_name}")
        self.embedding_model = SentenceTransformer(config.embedding_model_name)
        
        print(f"Loading cross-encoder: {config.cross_encoder_model_name}")
        self.cross_encoder = CrossEncoder(config.cross_encoder_model_name)
        
        self.store = QdrantStore()
        # Initialize collection if not exists (assume 384 dim for bge-small)
        # Note: BAAI/bge-small-en-v1.5 has dim 384
        self.store.setup_collection(vector_size=384)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        # Using sentence-transformers to encode
        # For BGE, we might need a prompt like "Represent this sentence for searching relevant passages: " for queries
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()

    def ingest(self, chunks: list[str], metadatas: list[dict] = None):
        """Embeds and ingests chunks into Qdrant."""
        if not chunks:
            return
        embeddings = self.embed_documents(chunks)
        self.store.add_documents(chunks, embeddings, metadatas)

    def retrieve(self, query: str, top_k: int = 5, rerank_top_k: int = 3) -> list[str]:
        """Retrieves and re-ranks top documents for a query."""
        # 1. Embed query
        # For bge models, query needs a prefix for better performance (usually "Represent this sentence for searching relevant passages: ")
        query_embedding = self.embedding_model.encode(f"Represent this sentence for searching relevant passages: {query}").tolist()
        
        # 2. Vector search (fetch more than needed for reranking)
        initial_results = self.store.search(query_embedding, limit=top_k)
        if not initial_results:
            return []
            
        retrieved_texts = [res["text"] for res in initial_results]
        
        # 3. Re-rank using cross-encoder
        cross_inp = [[query, text] for text in retrieved_texts]
        scores = self.cross_encoder.predict(cross_inp)
        
        # Sort based on scores
        ranked_results = sorted(zip(scores, retrieved_texts), key=lambda x: x[0], reverse=True)
        
        # Return the top N reranked texts
        return [text for score, text in ranked_results[:rerank_top_k]]
