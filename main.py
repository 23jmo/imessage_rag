import os
from dotenv import load_dotenv
from imessage_insight.utils import get_processed_messages_for_contact
from imessage_insight.chunking import chunk_messages
from imessage_insight.embedding import MessageEmbedder
from imessage_insight.vector_store import ChromaVectorStore
from imessage_insight.rag import RAGPipeline

load_dotenv()

# --- CLI Prompt Helpers ---
def prompt_choice(prompt, choices, default=None):
    print(f"{prompt} ({'/'.join(choices)})")
    val = input().strip().lower()
    if not val and default:
        return default
    while val not in choices:
        print(f"Please enter one of: {', '.join(choices)}")
        val = input().strip().lower()
    return val

def prompt_int(prompt, default):
    print(f"{prompt} (default: {default})")
    val = input().strip()
    if not val:
        return default
    try:
        return int(val)
    except ValueError:
        print("Invalid input, using default.")
        return default

def prompt_float(prompt, default):
    print(f"{prompt} (default: {default})")
    val = input().strip()
    if not val:
        return default
    try:
        return float(val)
    except ValueError:
        print("Invalid input, using default.")
        return default

# --- Main Workflow ---
def main():
    print("\n=== iMessage RAG CLI ===\n")
    contact = input("Enter the phone number or Apple ID of the contact (no spaces, include country code if phone): ").strip()
    if not contact:
        print("Contact is required.")
        return
    strategy = prompt_choice("Choose chunking strategy", ["fixed", "time", "timeandfixed"], default="time")
    chunk_size = prompt_int("Enter chunk size", 10)
    hours_gap = prompt_float("Enter hours gap for new chunk", 1.0)
    # Embedding model selection
    print("Select embedding model:")
    print("  1. SentenceTransformers (all-MiniLM-L6-v2) [default]")
    print("  2. OpenAI (text-embedding-ada-002)")
    emb_choice = input("Enter 1 or 2: ").strip() or "1"
    if emb_choice not in ("1", "2"):
        print("Invalid choice. Using SentenceTransformers.")
        emb_choice = "1"
    top_k = prompt_int("How many chunks to retrieve for each query?", 5)

    print(f"\nFetching and processing messages for: {contact} ...")
    try:
        processed = get_processed_messages_for_contact(contact)
    except Exception as e:
        print(f"Error fetching or processing messages: {e}")
        return
    if not processed:
        print("No messages found for this contact.")
        return
    print(f"Processed {len(processed)} messages. Chunking...\n")
    chunks = chunk_messages(
        processed,
        strategy=strategy,
        chunk_size=chunk_size,
        hours_gap=hours_gap
    )

    # --- Use a unique collection name for each embedding backend ---
    if emb_choice == "2":
        embedder = MessageEmbedder(backend='openai')
        collection_name = "imessage_chunks_openai"
    else:
        embedder = MessageEmbedder(backend='sentence_transformers')
        collection_name = "imessage_chunks"

    # --- Check if ChromaDB already has data for this collection ---
    store = ChromaVectorStore(collection_name=collection_name, persist_dir="imessage_insight/chromadb_data")
    existing = store.collection.count()
    if existing > 0:
        print(f"ChromaDB already contains {existing} chunks in collection '{collection_name}'. Skipping embedding and using existing data.")
        skip_embedding = True
    else:
        skip_embedding = False

    if not skip_embedding:
        print(f"Created {len(chunks)} chunks. Generating embeddings...\n")
        chunks_with_embeddings = embedder.generate_embeddings(chunks)
        store.add_chunks(chunks_with_embeddings)
        print(f"Stored {len(chunks_with_embeddings)} chunks in ChromaDB.\n")
    else:
        print("Using existing ChromaDB data for Q&A.\n")

    # --- Use unified RAGPipeline for both backends ---
    llm_model = 'gpt-4o' if emb_choice == "2" else 'gpt-3.5-turbo'
    rag = RAGPipeline(collection_name=collection_name, persist_dir="imessage_insight/chromadb_data", embedder=embedder, llm_model=llm_model)

    print("\n--- Ready for Q&A! ---\nType your question, or 'exit' to quit.")
    while True:
        query = input("\nYour question: ").strip()
        if query.lower() == 'exit':
            print("Goodbye!")
            break
        try:
            answer, context = rag.generate_answer(query, top_k=top_k)
            print("\n--- Answer ---")
            print(answer)
            print("\n--- Context Used ---")
            print(context)
        except Exception as e:
            print(f"Error during RAG Q&A: {e}")

if __name__ == "__main__":
    main()
