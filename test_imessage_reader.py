from imessage_reader import fetch_data
import os

# Default path to chat.db
DB_PATH = os.path.expanduser('~/Library/Messages/chat.db')

# Create a FetchData instance
fd = fetch_data.FetchData(DB_PATH)

# Get all messages: list of tuples (user id, message, service, ...)
my_data = fd.get_messages()

# Prompt user for a phone number or Apple ID to filter
search = input("Enter the contact's phone number or Apple ID to filter: ").strip()

# Normalize input (remove spaces, dashes, parentheses)
def normalize(s):
    import re
    return re.sub(r'\D', '', s) if s and s[0] != '+' else s.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')

search_norm = normalize(search)

# Filter messages where the user id matches the input (in any common format)
filtered = [msg for msg in my_data if search_norm in normalize(str(msg[0]))]

print(f"Total messages found for {search}: {len(filtered)}")
for msg in filtered[:20]:
    print(msg) 