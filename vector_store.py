import chromadb
from chromadb.config import Settings

class ChromaVectorStore:
    """
    Handles storage and retrieval of message chunk embeddings using ChromaDB.
    """
    def __init__(self, collection_name="imessage_chunks", persist_dir="chromadb_data"):
        # Initialize ChromaDB client and collection
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir
        ))
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_chunks(self, chunks):
        """
        Add message chunks (with embeddings) to the collection.
        Each chunk must have a unique 'id', 'embedding', and 'metadata'.
        """
        ids = [str(chunk['id']) for chunk in chunks]
        embeddings = [chunk['embedding'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def query(self, query_embedding, top_k=5):
        """
        Query the collection for the top_k most similar chunks to the query_embedding.
        Returns a list of dicts with text, metadata, and score.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        # Format results for easy use
        return [
            {
                "text": doc,
                "metadata": meta,
                "score": 1 - dist  # Chroma returns distance; convert to similarity
            }
            for doc, meta, dist in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0]
            )
        ] 