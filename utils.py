import re
from imessage_reader import fetch_data
from imessage_insight.message_preprocessor import MessagePreprocessor
import os

# --- Phone Number Normalization ---
def normalize(s):
    """
    Normalize phone numbers for matching.
    Removes non-digits unless the number starts with '+', in which case it strips spaces, parentheses, and dashes.
    """
    return re.sub(r'\D', '', s) if s and s[0] != '+' else s.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')

# --- Utility Function ---
def get_processed_messages_for_contact(contact):
    """
    Normalize the contact, fetch messages, and preprocess them.
    Returns a list of processed message dicts.
    """
    DB_PATH = os.path.expanduser('~/Library/Messages/chat.db')
    fd = fetch_data.FetchData(DB_PATH)
    all_messages = fd.get_messages()
    norm_contact = normalize(contact)

    # Filter messages for this contact
    messages = [msg for msg in all_messages if norm_contact in normalize(str(msg[0]))]

    preprocess_input = []
    for i, msg in enumerate(messages):
        # Defensive: skip if date or text is missing or invalid
        date_val = msg[2]
        text_val = msg[1]
        if not isinstance(date_val, str) or not date_val[:4].isdigit():
            continue
        if not isinstance(text_val, str) or not text_val.strip():
            continue
        is_from_me = bool(msg[5])
        preprocess_input.append((i, date_val, text_val, is_from_me))

    # Clean/process messages
    preprocessor = MessagePreprocessor()
    processed = preprocessor.process_messages(preprocess_input)
    processed.sort(key=lambda m: m['timestamp'])

    print(f"Total processed messages: {len(processed)}")
    return processed 