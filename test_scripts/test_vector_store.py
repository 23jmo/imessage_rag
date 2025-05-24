# Run this script with:
#   python -m imessage_insight.test_scripts.test_vector_store
# from the project root so that package imports work correctly.

from imessage_insight.utils import get_processed_messages_for_contact
from imessage_insight.chunking import chunk_messages
from imessage_insight.embedding import MessageEmbedder
from imessage_insight.vector_store import ChromaVectorStore

# --- Main Script ---
def main():
    # 1. Get real messages and chunk them
    contact = input("Enter contact for vector store test: ").strip()
    processed = get_processed_messages_for_contact(contact)
    if not processed:
        print("No messages found for this contact.")
        return
    chunks = chunk_messages(processed, strategy='timeandfixed', chunk_size=20, hours_gap=1)
    print(f"Chunked into {len(chunks)} chunks.")

    # 2. Generate embeddings
    embedder = MessageEmbedder()
    chunks = embedder.generate_embeddings(chunks)

    # 3. Store in ChromaDB
    store = ChromaVectorStore()
    store.add_chunks(chunks)
    print(f"Stored {len(chunks)} chunks in ChromaDB.")

    # 4. Query
    while True:
        query = input("\nEnter a test query (or 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            break
        query_embedding = embedder.model.encode([query])[0]
        results = store.query(query_embedding, top_k=5)
        print("\nTop results:")
        for idx, res in enumerate(results):
            print(f"\nResult {idx+1}:")
            print(f"Score: {res['score']:.3f}")
            print(f"Text: {res['text'][:100]}...")
            print(f"Metadata: {res['metadata']}")
            print(f"Chunk {idx+1} embedding type: {type(res['embedding'])}, shape: {getattr(res['embedding'], 'shape', 'unknown')}")

if __name__ == "__main__":
    main() 