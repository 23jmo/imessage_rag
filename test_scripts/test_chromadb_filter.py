# Test ChromaDB filtering by start_date_ts directly (bypassing LangChain retriever)
# Usage: python -m imessage_insight.test_scripts.test_chromadb_filter

from langchain_community.vectorstores import Chroma
from datetime import datetime
import os

CHROMA_DIR = "imessage_insight/chromadb_data"

if __name__ == "__main__":
    print("\n--- Test ChromaDB Filtering by start_date_ts ---\n")
    collection_name = input("Enter collection name (default: imessage_chunks): ").strip() or "imessage_chunks"
    cutoff_date = input("Enter cutoff date (YYYY-MM-DD): ").strip()
    try:
        cutoff_ts = datetime.fromisoformat(cutoff_date).timestamp()
    except Exception as e:
        print(f"Invalid date format: {e}")
        exit(1)
    print(f"Using cutoff_ts: {cutoff_ts} ({datetime.fromtimestamp(cutoff_ts).isoformat()})")

    # Load the vectorstore
    vectorstore = Chroma(
        collection_name=collection_name,
        persist_directory=CHROMA_DIR,
        embedding_function=None
    )
    # Query ChromaDB directly with the filter
    results = vectorstore._collection.get(
        where={"start_date_ts": {"$gt": cutoff_ts}},
        include=["metadatas", "documents"],
        limit=10
    )
    n = len(results["documents"])
    print(f"\nFound {n} chunks with start_date_ts > {cutoff_ts}:")
    for i, (meta, doc) in enumerate(zip(results["metadatas"], results["documents"])):
        print(f"Chunk {i+1}:")
        print(f"  Metadata: {meta}")
        print(f"  Text: {doc[:80]}...\n")
    if n == 0:
        print("No chunks matched the filter. Check your cutoff and metadata.") 