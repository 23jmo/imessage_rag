# Run this script with:
#   python -m imessage_insight.test_scripts.embed_real_chunks
# from the project root so that package imports work correctly.

from imessage_insight.utils import get_processed_messages_for_contact
from imessage_insight.chunking import chunk_messages
from imessage_insight.embedding import MessageEmbedder

# --- User Input ---
def get_user_input():
    print("Enter the phone number or Apple ID of the contact (no spaces, include country code if phone):")
    contact = input().strip()
    print("""
Choose chunking strategy:
  fixed        - Chunks are fixed-size (N messages per chunk)
  time         - Chunks are split by time gap (e.g., 1 hour)
  timeandfixed - Chunks are split by time gap, but also capped at a max size (best of both worlds)
(Default: time)
""")
    strategy = input().strip().lower() or 'time'
    chunk_size = 10
    hours_gap = 1
    if strategy == 'fixed' or strategy == 'timeandfixed':
        print("Enter chunk size (default: 10):")
        try:
            chunk_size = int(input().strip() or 10)
        except ValueError:
            chunk_size = 10
    if strategy == 'time' or strategy == 'timeandfixed':
        print("Enter hours gap for new chunk (default: 1):")
        try:
            hours_gap = float(input().strip() or 1)
        except ValueError:
            hours_gap = 1
    return contact, strategy, chunk_size, hours_gap

# --- Main Script ---
def main():
    contact, strategy, chunk_size, hours_gap = get_user_input()
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
    # Chunk messages
    chunks = chunk_messages(
        processed,
        strategy=strategy,
        chunk_size=chunk_size,
        hours_gap=hours_gap
    )
    print(f"Created {len(chunks)} chunks. Generating embeddings...\n")
    # Generate embeddings
    embedder = MessageEmbedder()
    chunks_with_embeddings = embedder.generate_embeddings(chunks)
    for idx, chunk in enumerate(chunks_with_embeddings):
        emb = chunk.get('embedding')
        print(f"Chunk {idx+1} embedding type: {type(emb)}, shape: {getattr(emb, 'shape', 'unknown')}")
        print(f"Text preview: {chunk['text'][:80]}...\n")
    print(f"\nDone. Embedded {len(chunks_with_embeddings)} chunks for contact: {contact}")

if __name__ == "__main__":
    main() 