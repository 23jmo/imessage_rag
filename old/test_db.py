from imessage_insight.old.imessage_db import MessageDatabaseConnector
from message_preprocessor import MessagePreprocessor
from pprint import pprint

# Prompt user for contact (phone number or Apple ID)
target_contact = input("Enter the contact's phone number or Apple ID: ")

db = MessageDatabaseConnector()
if db.connect():
    # Show the normalized contact string
    normalized = db.normalize_contact(target_contact)
    print(f"Normalized contact: {normalized}")

    # Print all chat IDs and handles for the contact
    handle_ids = db.get_all_handle_ids(target_contact)
    print(f"[DEBUG] Target handle_ids: {handle_ids}")
    cursor = db.connection.cursor()
    all_target_chat_ids = set()
    for target_id in handle_ids:
        cursor.execute("SELECT chat_id FROM chat_handle_join WHERE handle_id = ?", (target_id,))
        for (chat_id,) in cursor.fetchall():
            all_target_chat_ids.add(chat_id)
    print(f"[DEBUG] All chat_ids for target: {all_target_chat_ids}")
    for chat_id in all_target_chat_ids:
        cursor.execute("SELECT handle_id FROM chat_handle_join WHERE chat_id = ?", (chat_id,))
        handles = set(row[0] for row in cursor.fetchall())
        print(f"[DEBUG] chat_id {chat_id} has handles: {handles}")

    # Fetch all direct (1:1) chat messages with the contact
    messages = db.get_direct_chat_messages(target_contact)
    print(f"Total direct (1:1) chat messages found: {len(messages)}")

    # Process and clean messages
    preprocessor = MessagePreprocessor()
    processed = preprocessor.process_messages(messages)
    # Globally sort by timestamp
    processed.sort(key=lambda m: m['timestamp'])
    print(f"Total processed messages: {len(processed)}")
    print("First 20 processed messages:")
    pprint(processed[:20])
    db.close()
else:
    print("Failed to connect to the database. Check permissions and path.") 