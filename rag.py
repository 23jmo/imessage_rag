import os
from openai import OpenAI
from imessage_insight.vector_store import ChromaVectorStore
from dotenv import load_dotenv

load_dotenv()

class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for iMessage insight.
    Handles embedding, retrieval, and LLM answer generation.
    """
    def __init__(self, collection_name="imessage_chunks", persist_dir="chromadb_data", embedder=None, llm_model="gpt-4o"):
        if embedder is None:
            raise ValueError("RAGPipeline requires an embedder instance.")
        self.embedder = embedder
        self.vector_store = ChromaVectorStore(collection_name=collection_name, persist_dir=persist_dir)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment.")
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.llm_model = llm_model

    def retrieve_context(self, query, top_k=5):
        """
        Embed the query and retrieve top-k most similar chunks from ChromaDB.
        Returns a list of dicts with text and metadata.
        """
        # Use the embedder's backend to embed the query
        if hasattr(self.embedder, 'backend') and self.embedder.backend == 'openai':
            query_embedding = self.embedder.model.embed_query(query)
        else:
            query_embedding = self.embedder.model.encode([query])[0]
        results = self.vector_store.query(query_embedding, top_k=top_k)
        return results

    def generate_answer(self, query, top_k=5, max_context_chars=3000):
        """
        Retrieve context and generate an answer using OpenAI LLM.
        Returns the answer string and the context used.
        """
        retrieved = self.retrieve_context(query, top_k=top_k)
        context_chunks = [r['text'] for r in retrieved]
        context = "\n---\n".join(context_chunks)
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "..."
        prompt = f"""
Context:
{context}

Question: {query}
Answer:"""
        response = self.openai_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided iMessage conversation context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.2
        )
        answer = response.choices[0].message.content.strip()
        return answer, context 