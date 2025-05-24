import re
from datetime import datetime

class MessagePreprocessor:
    """
    Handles cleaning and normalization of message text, timestamp conversion,
    and filtering out empty or corrupted messages.
    """
    def __init__(self):
        pass

    def clean_text(self, text):
        """
        Clean and normalize message text.
        Removes extra whitespace and special characters.
        Returns a cleaned string or empty string if invalid.
        """
        if not text:
            return ""
        # Convert None to empty string
        text = text or ""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def convert_imessage_date(self, timestamp):
        """
        Convert iMessage timestamp (nanoseconds since 2001-01-01) to datetime or return string if already formatted.
        Returns a datetime object, string, or None if invalid.
        """
        if not timestamp:
            return None
        # If already a string (from imessage_reader), just return as is
        if isinstance(timestamp, str):
            return timestamp
        # Otherwise, treat as nanoseconds since 2001-01-01
        mac_epoch_start = 978307200  # 2001-01-01 00:00:00 UTC
        unix_timestamp = (timestamp / 1e9) + mac_epoch_start
        try:
            return datetime.fromtimestamp(unix_timestamp)
        except Exception:
            return None

    def process_messages(self, raw_messages):
        """
        Process a list of raw messages from the database.
        Cleans text, converts timestamps, and filters out empty messages.
        Returns a list of dicts with id, timestamp, text, is_from_me.
        """
        processed_messages = []
        for msg_id, date, text, is_from_me in raw_messages:
            clean_text = self.clean_text(text)
            # Skip empty messages
            if not clean_text:
                continue
            # Convert timestamp
            timestamp = self.convert_imessage_date(date)
            processed_messages.append({
                'id': msg_id,
                'timestamp': timestamp,
                'text': clean_text,
                'is_from_me': bool(is_from_me)
            })
        return processed_messages 