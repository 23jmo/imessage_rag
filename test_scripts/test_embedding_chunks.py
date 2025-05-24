import sys
import os
from datetime import datetime, timedelta


# Ensure the parent directory is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from imessage_insight.embedding import MessageEmbedder
from imessage_insight.chunking import chunk_messages

# --- Test Data ---
def make_test_messages():
    """
    Generate a list of test messages with timestamps and alternating senders.
    """
    base_time = datetime(2023, 1, 1, 12, 0, 0)
    messages = []
    for i in range(15):
        # Alternate sender
        is_from_me = (i % 2 == 0)
        # Create time gaps every 5 messages
        if i == 5:
            msg_time = base_time + timedelta(hours=2)
        elif i == 10:
            msg_time = base_time + timedelta(hours=5)
        else:
            msg_time = base_time + timedelta(minutes=i)
        messages.append({
            'id': i,
            'timestamp': msg_time.isoformat(),
            'text': f"Test message {i}",
            'is_from_me': is_from_me
        })
    return messages

# --- Test Functions ---
def test_fixed_size():
    print("\n--- Testing Fixed-Size Chunking ---")
    messages = make_test_messages()
    chunks = chunk_messages(messages, strategy='fixed', chunk_size=4)
    for idx, chunk in enumerate(chunks):
        print(f"\nChunk {idx+1}:")
        print(f"Text:\n{chunk['text']}")
        print(f"Metadata: {chunk['metadata']}")

def test_time_based():
    print("\n--- Testing Time-Based Chunking ---")
    messages = make_test_messages()
    chunks = chunk_messages(messages, strategy='time', hours_gap=1)
    for idx, chunk in enumerate(chunks):
        print(f"\nChunk {idx+1}:")
        print(f"Text:\n{chunk['text']}")
        print(f"Metadata: {chunk['metadata']}")

def test_edge_cases():
    print("\n--- Testing Edge Cases ---")
    # Empty list
    empty = chunk_messages([], strategy='fixed', chunk_size=3)
    print(f"Empty input (fixed): {empty}")
    # Single message
    single = chunk_messages([
        {'id': 1, 'timestamp': datetime.now().isoformat(), 'text': 'Hello', 'is_from_me': True}
    ], strategy='time', hours_gap=1)
    print(f"Single message (time): {single}")

def test_embedding_on_real_chunks():
    print("\n--- Testing Embedding Generation on Real Chunks ---")
    # Generate test messages and chunk them
    messages = make_test_messages()
    chunks = chunk_messages(messages, strategy='fixed', chunk_size=4)
    # Initialize embedder
    embedder = MessageEmbedder()
    # Generate embeddings
    chunks_with_embeddings = embedder.generate_embeddings(chunks)
    for idx, chunk in enumerate(chunks_with_embeddings):
        emb = chunk.get('embedding')
        print(f"Chunk {idx+1} embedding type: {type(emb)}, shape: {getattr(emb, 'shape', 'unknown')}")
        print(f"Text: {chunk['text'][:40]}...\n")

if __name__ == "__main__":
    test_fixed_size()
    test_time_based()
    test_edge_cases()
    test_embedding_on_real_chunks() 