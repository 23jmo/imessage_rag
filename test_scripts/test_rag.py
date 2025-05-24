# Run this script with:
#   python -m imessage_insight.test_scripts.test_rag
# from the project root so that package imports work correctly.

from imessage_insight.rag import RAGPipeline

# --- Main Script ---
def main():
    print("\n--- iMessage RAG Q&A ---")
    print("Make sure you have already stored chunks and embeddings in ChromaDB.")
    rag = RAGPipeline()
    while True:
        query = input("\nEnter your question (or 'exit' to quit): ").strip()
        if query.lower() == 'exit':
            break
        print("\nRetrieving context and generating answer...\n")
        try:
            answer, context = rag.generate_answer(query, top_k=5)
        except Exception as e:
            print(f"Error: {e}")
            continue
        print("--- Answer ---")
        print(answer)
        print("\n--- Context Used ---")
        print(context)

if __name__ == "__main__":
    main() 