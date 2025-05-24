# Run this script with:
#   python -m imessage_insight.test_scripts.inspect_chromadb
# from the project root so that package imports work correctly.

from imessage_insight.vector_store import ChromaVectorStore

# --- Main Script ---
def main():
    store = ChromaVectorStore()
    collection = store.collection
    print(f"Collection name: {collection.name}")
    print(f"Number of items: {collection.count()}")

    # Fetch a sample of the stored items
    print("\nSample items:")
    results = collection.get(include=["documents", "metadatas"], limit=5)
    for i in range(len(results["ids"])):
        print(f"\nID: {results['ids'][i]}")
        print(f"Text: {results['documents'][i][:100]}...")
        print(f"Metadata: {results['metadatas'][i]}")

if __name__ == "__main__":
    main() 