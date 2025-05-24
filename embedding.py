from sentence_transformers import SentenceTransformer
import numpy as np

class MessageEmbedder:
    """
    Handles embedding generation for message chunks using SentenceTransformers.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the embedding model.
        """
        print(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, chunks):
        """
        Generate embeddings for a list of message chunks.
        Adds an 'embedding' field to each chunk dict.
        Returns the list of chunks with embeddings.
        """
        texts = [chunk['text'] for chunk in chunks]
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
        return chunks
      