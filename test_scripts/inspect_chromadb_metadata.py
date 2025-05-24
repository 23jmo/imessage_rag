# Inspect ChromaDB collection metadata (e.g., start_date_ts)
# Usage: python -m imessage_insight.test_scripts.inspect_chromadb_metadata

from langchain_community.vectorstores import Chroma
import os
from datetime import datetime

CHROMA_DIR = "imessage_insight/chromadb_data"

if __name__ == "__main__":
    print("\n--- Inspect ChromaDB Collection Metadata ---\n")
    collection_name = input("Enter collection name (default: imessage_chunks): ").strip() or "imessage_chunks"
    print(f"Inspecting collection: {collection_name}\n")

    # Load the vectorstore
    vectorstore = Chroma(
        collection_name=collection_name,
        persist_directory=CHROMA_DIR,
        embedding_function=None  # Not needed for metadata inspection
    )
    # Get a sample for preview
    docs = vectorstore._collection.get(include=["metadatas", "documents"], limit=10)
    total = vectorstore._collection.count()
    print(f"Total chunks in collection: {total}\n")
    for i, (meta, doc) in enumerate(zip(docs["metadatas"], docs["documents"])):
        print(f"Chunk {i+1}:")
        print(f"  Metadata: {meta}")
        print(f"  Text: {doc[:80]}...\n")
    if total > 10:
        print(f"... (showing first 10 of {total} chunks)")

    # Scan all metadatas for start_date_ts
    print("\n--- Scanning all chunks for start_date_ts range ---")
    all_docs = vectorstore._collection.get(include=["metadatas"], limit=total)
    ts_values = []
    for meta in all_docs["metadatas"]:
        ts = meta.get("start_date_ts")
        if isinstance(ts, (float, int)):
            ts_values.append(ts)
    if ts_values:
        min_ts = min(ts_values)
        max_ts = max(ts_values)
        print(f"Found {len(ts_values)} chunks with start_date_ts.")
        print(f"Min start_date_ts: {min_ts} ({datetime.fromtimestamp(min_ts).isoformat()})")
        print(f"Max start_date_ts: {max_ts} ({datetime.fromtimestamp(max_ts).isoformat()})")
    else:
        print("No valid start_date_ts values found in metadata.") 