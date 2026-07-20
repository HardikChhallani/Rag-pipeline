from qdrant_client import QdrantClient
from qdrant_client.http import models
from config import config

class QdrantStore:
    def __init__(self):
        # Initialize Qdrant Client (local or remote based on config)
        if config.qdrant_url.startswith("http"):
            self.client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key)
        else:
            # Fallback to local memory/disk if it's a local path
            self.client = QdrantClient(path=config.qdrant_url if config.qdrant_url != "http://localhost:6333" else ":memory:")
            
        self.collection_name = config.collection_name

    def setup_collection(self, vector_size: int = 384):
        """Creates the collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
            )
            print(f"Collection {self.collection_name} created.")

    def add_documents(self, documents: list[str], embeddings: list[list[float]], metadatas: list[dict] = None):
        """Adds documents and their embeddings to Qdrant."""
        if not metadatas:
            metadatas = [{"text": doc} for doc in documents]
        else:
            for i, doc in enumerate(documents):
                metadatas[i]["text"] = doc

        points = [
            models.PointStruct(
                id=i, 
                vector=embeddings[i],
                payload=metadatas[i]
            )
            for i in range(len(documents))
        ]
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Added {len(documents)} documents to Qdrant.")

    def search(self, query_vector: list[float], limit: int = 5):
        """Searches for the closest vectors."""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )
        # Return list of text and score
        return [{"text": hit.payload.get("text", ""), "score": hit.score, "metadata": hit.payload} for hit in results]
