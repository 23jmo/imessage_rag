import chromadb
from datetime import datetime
import os

# --- Config ---
CHROMA_DIR = "imessage_insight/chromadb_data"
BATCH_SIZE = 100  # Adjust as needed

def iso_to_timestamp(iso_str):
    try:
        return datetime.fromisoformat(iso_str).timestamp()
    except Exception:
        return None

def main():
    collection_name = input("Enter collection name (default: imessage_chunks): ").strip() or "imessage_chunks"
    print(f"Opening ChromaDB collection '{collection_name}' in '{CHROMA_DIR}'...")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(collection_name)

    # Get all document IDs
    all_ids = collection.get(include=["metadatas"])['ids']
    print(f"Found {len(all_ids)} documents.")

    updated = 0
    missing = 0
    for i in range(0, len(all_ids), BATCH_SIZE):
        batch_ids = all_ids[i:i+BATCH_SIZE]
        batch = collection.get(ids=batch_ids, include=["metadatas"])
        metadatas = batch["metadatas"]
        ids = batch["ids"]
        new_metadatas = []
        for meta, doc_id in zip(metadatas, ids):
            print(f"\n[BEFORE] Document {doc_id} metadata: {meta}")
            meta = dict(meta)  # Work on a copy
            start_date = meta.get("start_date")
            if not start_date:
                print(f"[WARN] Document {doc_id} missing 'start_date'. Skipping.")
                missing += 1
                new_metadatas.append(meta)
                continue
            ts = iso_to_timestamp(start_date)
            if ts is None:
                print(f"[WARN] Document {doc_id} has invalid 'start_date': {start_date}. Skipping.")
                missing += 1
                new_metadatas.append(meta)
                continue
            # Always set start_date_ts as a float inside the metadata dict
            meta["start_date_ts"] = ts
            updated += 1
            print(f"[AFTER]  Document {doc_id} metadata: {meta}")
            new_metadatas.append(meta)
        # Update metadatas in collection
        collection.update(ids=ids, metadatas=new_metadatas)
    print(f"\nUpdate complete.")
    print(f"Documents updated: {updated}")
    print(f"Documents missing/invalid 'start_date': {missing}")

if __name__ == "__main__":
    main() 