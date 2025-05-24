from sentence_transformers import SentenceTransformer
import numpy as np
import os

# Import OpenAIEmbeddings only if needed to avoid unnecessary dependency for local users
try:
    from langchain_openai import OpenAIEmbeddings
except ImportError:
    OpenAIEmbeddings = None

class MessageEmbedder:
    """
    Handles embedding generation for message chunks using SentenceTransformers or OpenAI.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2', backend='sentence_transformers'):
        """
        Initialize the embedding model. backend: 'sentence_transformers' or 'openai'.
        """
        self.backend = backend
        self.model_name = model_name
        if backend == 'sentence_transformers':
            print(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
        elif backend == 'openai':
            if OpenAIEmbeddings is None:
                raise ImportError("langchain_openai is not installed. Please install it to use OpenAI embeddings.")
            print("Using OpenAIEmbeddings (text-embedding-ada-002)")
            self.model = OpenAIEmbeddings()
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def generate_embeddings(self, chunks):
        """
        Generate embeddings for a list of message chunks.
        Adds an 'embedding' field to each chunk dict (as a list for ChromaDB compatibility).
        Returns the list of chunks with embeddings.
        """
        texts = [chunk['text'] for chunk in chunks]
        print(f"Generating embeddings for {len(texts)} chunks using {self.backend}...")
        if self.backend == 'sentence_transformers':
            embeddings = self.model.encode(texts, show_progress_bar=True)
        elif self.backend == 'openai':
            embeddings = self.model.embed_documents(texts)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i] if isinstance(embeddings[i], list) else embeddings[i].tolist()
        return chunks

    def get_dimension(self):
        if self.backend == 'sentence_transformers':
            return self.model.get_sentence_embedding_dimension()
        elif self.backend == 'openai':
            return 1536  # text-embedding-ada-002
        else:
            return None
      