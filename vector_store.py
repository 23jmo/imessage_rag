import chromadb
import numpy as np  # For type checking
from datetime import datetime

class ChromaVectorStore:
    """
    Handles storage and retrieval of message chunk embeddings using ChromaDB.
    Uses PersistentClient for on-disk persistence (see ChromaDB docs).
    """
    def __init__(self, collection_name="imessage_chunks", persist_dir="imessage_insight/chromadb_data"):
        # Use PersistentClient for on-disk persistence
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)

    def _ensure_list(self, embedding):
        """
        Helper to ensure an embedding is a plain Python list (not a numpy array).
        """
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        return embedding

    def _ensure_start_date_ts(self, meta):
        """
        Ensure 'start_date_ts' is present and correct in metadata.
        If 'start_date' is present, compute its timestamp and add as 'start_date_ts'.
        """
        start_date = meta.get("start_date")
        if start_date:
            try:
                ts = datetime.fromisoformat(start_date).timestamp()
                old_ts = meta.get("start_date_ts")
                # Fix type if string
                if isinstance(old_ts, str):
                    try:
                        old_ts_float = float(old_ts)
                        if old_ts_float == ts:
                            meta = dict(meta)
                            meta["start_date_ts"] = ts
                            return meta
                    except Exception:
                        pass
                if old_ts != ts:
                    meta = dict(meta)
                    meta["start_date_ts"] = ts
            except Exception:
                pass
        return meta

    def add_chunks(self, chunks):
        """
        Add message chunks (with embeddings) to the collection.
        Each chunk must have a unique 'id', 'embedding', and 'metadata'.
        Ensures all embeddings are lists for ChromaDB compatibility.
        Ensures 'start_date_ts' is present and correct in metadata.
        Automatically persists the client so data is written to disk.
        """
        ids = [str(chunk['id']) for chunk in chunks]
        # Ensure all embeddings are lists
        embeddings = [self._ensure_list(chunk['embedding']) for chunk in chunks]
        # Ensure all metadatas have start_date_ts
        metadatas = [self._ensure_start_date_ts(chunk['metadata']) for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        # Persistence is automatic with PersistentClient

    def query(self, query_embedding, top_k=5):
        """
        Query the collection for the top_k most similar chunks to the query_embedding.
        Ensures the query embedding is a list for ChromaDB compatibility.
        Returns a list of dicts with text, metadata, score, and embedding.
        """
        query_embedding = self._ensure_list(query_embedding)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances", "embeddings"]  # Include embeddings
        )
        # Format results for easy use, including embedding
        return [
            {
                "text": doc,
                "metadata": meta,
                "score": 1 - dist,  # Chroma returns distance; convert to similarity
                "embedding": emb
            }
            for doc, meta, dist, emb in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0], results["embeddings"][0]
            )
        ] 