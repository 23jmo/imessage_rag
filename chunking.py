from datetime import datetime, timedelta

# --- Message Chunking Strategies ---

def chunk_by_fixed_size(messages, chunk_size=10):
    """
    Chunk messages into fixed-size groups.
    Each chunk contains up to `chunk_size` messages.
    Adds metadata: start_date, end_date, message_count.
    """
    chunks = []
    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i+chunk_size]
        # Join messages into a single text block
        chunk_text = "\n".join([
            f"{'Me' if msg['is_from_me'] else 'Friend'}: {msg['text']}" for msg in chunk
        ])
        chunks.append({
            'text': chunk_text,
            'metadata': {
                'start_date': chunk[0]['timestamp'],
                'end_date': chunk[-1]['timestamp'],
                'message_count': len(chunk)
            }
        })
    return chunks

def chunk_by_time(messages, hours_gap=1):
    """
    Chunk messages based on time gaps.
    A new chunk starts if the gap between messages exceeds `hours_gap`.
    Adds metadata: start_date, end_date, message_count.
    """
    if not messages:
        return []
    chunks = []
    current_chunk = [messages[0]]
    for i in range(1, len(messages)):
        prev = messages[i-1]
        curr = messages[i]
        # Convert to datetime if needed
        prev_time = prev['timestamp']
        curr_time = curr['timestamp']
        if isinstance(prev_time, str):
            prev_time = datetime.fromisoformat(prev_time)
        if isinstance(curr_time, str):
            curr_time = datetime.fromisoformat(curr_time)
        # If time gap exceeds threshold, start a new chunk
        if (curr_time - prev_time) > timedelta(hours=hours_gap):
            chunk_text = "\n".join([
                f"{'Me' if msg['is_from_me'] else 'Friend'}: {msg['text']}" for msg in current_chunk
            ])
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'start_date': current_chunk[0]['timestamp'],
                    'end_date': current_chunk[-1]['timestamp'],
                    'message_count': len(current_chunk)
                }
            })
            current_chunk = [curr]
        else:
            current_chunk.append(curr)
    # Add the last chunk
    if current_chunk:
        chunk_text = "\n".join([
            f"{'Me' if msg['is_from_me'] else 'Friend'}: {msg['text']}" for msg in current_chunk
        ])
        chunks.append({
            'text': chunk_text,
            'metadata': {
                'start_date': current_chunk[0]['timestamp'],
                'end_date': current_chunk[-1]['timestamp'],
                'message_count': len(current_chunk)
            }
        })
    return chunks

# --- New: Time-and-Fixed Chunking ---
def chunk_by_time_and_fixed(messages, hours_gap=1, max_chunk_size=20):
    """
    Chunk messages by time gap, but cap each chunk at max_chunk_size messages.
    Starts a new chunk if the time gap is exceeded or the chunk size limit is reached.
    Adds metadata: start_date, end_date, message_count.
    """
    if not messages:
        return []
    chunks = []
    current_chunk = [messages[0]]
    for i in range(1, len(messages)):
        prev = messages[i-1]
        curr = messages[i]
        # Convert to datetime if needed
        prev_time = prev['timestamp']
        curr_time = curr['timestamp']
        if isinstance(prev_time, str):
            prev_time = datetime.fromisoformat(prev_time)
        if isinstance(curr_time, str):
            curr_time = datetime.fromisoformat(curr_time)
        # Start new chunk if time gap exceeded or chunk size limit reached
        if (curr_time - prev_time) > timedelta(hours=hours_gap) or len(current_chunk) >= max_chunk_size:
            chunk_text = "\n".join([
                f"{'Me' if msg['is_from_me'] else 'Friend'}: {msg['text']}" for msg in current_chunk
            ])
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'start_date': current_chunk[0]['timestamp'],
                    'end_date': current_chunk[-1]['timestamp'],
                    'message_count': len(current_chunk)
                }
            })
            current_chunk = [curr]
        else:
            current_chunk.append(curr)
    # Add the last chunk
    if current_chunk:
        chunk_text = "\n".join([
            f"{'Me' if msg['is_from_me'] else 'Friend'}: {msg['text']}" for msg in current_chunk
        ])
        chunks.append({
            'text': chunk_text,
            'metadata': {
                'start_date': current_chunk[0]['timestamp'],
                'end_date': current_chunk[-1]['timestamp'],
                'message_count': len(current_chunk)
            }
        })
    return chunks

def chunk_messages(messages, strategy='time', chunk_size=10, hours_gap=1):
    """
    Main entry point for chunking messages.
    Selects the chunking strategy based on config.
    - strategy: 'fixed', 'time', or 'timeandfixed'
    - chunk_size: used for 'fixed' and as max_chunk_size for 'timeandfixed'
    - hours_gap: used for 'time' and 'timeandfixed'
    Returns a list of chunk dicts with text and metadata.
    """
    if strategy == 'fixed':
        return chunk_by_fixed_size(messages, chunk_size)
    elif strategy == 'time':
        return chunk_by_time(messages, hours_gap)
    elif strategy == 'timeandfixed':
        return chunk_by_time_and_fixed(messages, hours_gap=hours_gap, max_chunk_size=chunk_size)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}") 