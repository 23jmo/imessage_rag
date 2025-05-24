from message_preprocessor import MessagePreprocessor
from pprint import pprint

# Sample raw messages: (id, date, text, is_from_me)
sample_messages = [
    (1, 656789123456789000, '   Hello!   ', 1),
    (2, 656789123456800000, '\n\nHow are you?\t', 0),
    (3, 656789123456900000, '', 1),  # Empty
    (4, 656789123457000000, None, 0),  # None
    (5, 656789123457100000, '   ', 1),  # Whitespace only
    (6, 656789123457200000, 'Let\'s meet at 5pm! 😊', 0),
    (7, 656789123457300000, 'Special\u200bChar', 1),
]

preprocessor = MessagePreprocessor()
processed = preprocessor.process_messages(sample_messages)

print("Processed messages:")
pprint(processed) 