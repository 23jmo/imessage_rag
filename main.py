from imessage_reader import fetch_data
from message_preprocessor import MessagePreprocessor
from pprint import pprint
import os
import re

# Path to chat.db
DB_PATH = os.path.expanduser('~/Library/Messages/chat.db')

# Prompt user for contact
contact = input("Enter the contact's phone number or Apple ID: ").strip()

def normalize(s):
    # Normalize phone numbers for matching
    return re.sub(r'\D', '', s) if s and s[0] != '+' else s.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')

# Fetch all messages using imessage_reader
fd = fetch_data.FetchData(DB_PATH)
all_messages = fd.get_messages()  # Each message: (user id, message, service, ...)

# Filter messages by contact
contact_norm = normalize(contact)
filtered = [msg for msg in all_messages if contact_norm in normalize(str(msg[0]))]

print(f"Total messages found for {contact}: {len(filtered)}")

# Prepare messages for preprocessing: (id, date, text, is_from_me)
# imessage_reader returns: (user id, message, service, date, ...)
preprocess_input = []
for i, msg in enumerate(filtered):
    # id: i (or msg index), date: msg[3], text: msg[1], is_from_me: guess from service or user id
    preprocess_input.append((i, msg[3], msg[1], False if contact_norm in normalize(str(msg[0])) else True))

# Clean/process messages
preprocessor = MessagePreprocessor()
processed = preprocessor.process_messages(preprocess_input)
processed.sort(key=lambda m: m['timestamp'])

print(f"Total processed messages: {len(processed)}")
print("First 20 processed messages:")
pprint(processed[:20])
