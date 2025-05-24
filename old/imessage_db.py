import sqlite3
import os
import re
from typing import List

class MessageDatabaseConnector:
    """
    Handles connection to the macOS Messages chat.db and provides methods to
    retrieve handle IDs and messages for a given contact.
    """
    def __init__(self):
        # Path to the Messages database
        self.db_path = os.path.expanduser("~/Library/Messages/chat.db")
        self.connection = None

    def connect(self):
        """
        Connect to the chat.db SQLite database.
        Returns True if successful, False otherwise.
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            print("Make sure to grant Full Disk Access to the Terminal/Python in System Settings.")
            return False

    def normalize_contact(self, contact):
        """
        Normalize phone numbers to E.164 format (e.g., +16176822859).
        Accepts numbers with/without country code, spaces, dashes, parentheses.
        Returns the normalized string or the original if not a phone number.
        """
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', contact)
        # If it looks like a US number (10 digits), add +1
        if len(digits) == 10:
            return f'+1{digits}'
        # If it starts with 1 and is 11 digits, add +
        if len(digits) == 11 and digits.startswith('1'):
            return f'+{digits}'
        # If it starts with country code (e.g., +44...), keep as is
        if contact.startswith('+') and len(digits) > 10:
            return contact
        # Otherwise, return as is (could be Apple ID/email)
        return contact

    def get_all_handle_ids(self, target_contact) -> List[int]:
        """
        Find all handle IDs that match the normalized digits of the input.
        Returns a list of handle ROWIDs.
        """
        normalized = self.normalize_contact(target_contact)
        digits = re.sub(r'\D', '', normalized)
        cursor = self.connection.cursor()
        # Match any handle whose digits end with the last 7-10 digits (to catch all variations)
        like_patterns = [f'%{digits[-n:]}' for n in range(7, min(11, len(digits)+1))]
        handle_ids = set()
        for pattern in like_patterns:
            cursor.execute("SELECT ROWID FROM handle WHERE id LIKE ?", (pattern,))
            handle_ids.update([row[0] for row in cursor.fetchall()])
        return list(handle_ids)

    def get_handle_id(self, target_contact):
        """
        Get the handle_id for a given phone number or Apple ID.
        Returns the handle_id (int) or None if not found.
        """
        contact = self.normalize_contact(target_contact)
        cursor = self.connection.cursor()
        query = "SELECT ROWID FROM handle WHERE id = ?"
        cursor.execute(query, (contact,))
        result = cursor.fetchone()
        return result[0] if result else None

    def get_messages(self, handle_ids):
        """
        Get all messages for a list of handle_ids.
        Returns a list of tuples: (ROWID, date, text, is_from_me)
        """
        if not handle_ids:
            return []
        cursor = self.connection.cursor()
        # Use SQL IN clause to fetch messages for all handle_ids
        placeholders = ','.join(['?'] * len(handle_ids))
        query = f"""
        SELECT 
            message.ROWID, 
            message.date, 
            message.text, 
            message.is_from_me 
        FROM 
            message 
        JOIN 
            chat_message_join ON message.ROWID = chat_message_join.message_id 
        JOIN 
            chat_handle_join ON chat_message_join.chat_id = chat_handle_join.chat_id 
        WHERE 
            chat_handle_join.handle_id IN ({placeholders}) 
            AND message.text IS NOT NULL 
        ORDER BY 
            message.date ASC
        """
        cursor.execute(query, handle_ids)
        return cursor.fetchall()

    def get_my_handle_ids(self):
        """
        Attempt to infer the user's own handle IDs by looking at messages sent by the user (is_from_me=1).
        Returns a set of handle IDs.
        """
        cursor = self.connection.cursor()
        # Find all handle_ids that appear in chats where the user has sent messages
        cursor.execute('''
            SELECT DISTINCT chj.handle_id
            FROM message m
            JOIN chat_message_join cmj ON m.ROWID = cmj.message_id
            JOIN chat_handle_join chj ON cmj.chat_id = chj.chat_id
            WHERE m.is_from_me = 1 AND chj.handle_id IS NOT NULL
        ''')
        return set(row[0] for row in cursor.fetchall())

    def get_direct_chat_messages(self, target_contact):
        """
        Get all messages (sent and received) from 1:1 (non-group) chats with the contact.
        Returns a list of tuples: (ROWID, date, text, is_from_me)
        """
        handle_ids = self.get_all_handle_ids(target_contact)
        print(f"[DEBUG] Target handle_ids: {handle_ids}")
        if not handle_ids:
            return []
        my_handle_ids = self.get_my_handle_ids()
        print(f"[DEBUG] My handle_ids: {my_handle_ids}")
        if not my_handle_ids:
            print("Warning: Could not infer your own handle IDs. Results may be incomplete.")
        cursor = self.connection.cursor()
        # More flexible: treat as 1:1 if all handles are either mine or the target's, and both are present
        chat_ids = set()
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
            # Flexible check: all handles are either mine or the target's, and both are present
            if handles.issubset(my_handle_ids.union(set(handle_ids))) and any(h in my_handle_ids for h in handles) and any(h in handle_ids for h in handles):
                print(f"[DEBUG] chat_id {chat_id} selected as 1:1 chat (flexible)")
                chat_ids.add(chat_id)
        print(f"[DEBUG] Selected 1:1 chat_ids: {chat_ids}")
        if not chat_ids:
            return []
        chat_placeholders = ','.join(['?'] * len(chat_ids))
        msg_query = f'''
            SELECT 
                message.ROWID, 
                message.date, 
                message.text, 
                message.is_from_me 
            FROM 
                message 
            JOIN 
                chat_message_join ON message.ROWID = chat_message_join.message_id 
            WHERE 
                chat_message_join.chat_id IN ({chat_placeholders})
                AND message.text IS NOT NULL 
            ORDER BY 
                message.date ASC
        '''
        cursor.execute(msg_query, list(chat_ids))
        return cursor.fetchall()

    def close(self):
        """
        Close the database connection if open.
        """
        if self.connection:
            self.connection.close() 