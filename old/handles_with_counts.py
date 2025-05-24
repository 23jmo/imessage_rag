from imessage_insight.old.imessage_db import MessageDatabaseConnector

# Connect to the database

db = MessageDatabaseConnector()
if db.connect():
    cursor = db.connection.cursor()
    # Query to get all handles and their message counts
    query = '''
    SELECT 
        handle.ROWID, 
        handle.id, 
        COUNT(message.ROWID) as message_count
    FROM handle
    LEFT JOIN chat_handle_join ON handle.ROWID = chat_handle_join.handle_id
    LEFT JOIN chat_message_join ON chat_handle_join.chat_id = chat_message_join.chat_id
    LEFT JOIN message ON chat_message_join.message_id = message.ROWID AND message.text IS NOT NULL
    GROUP BY handle.ROWID, handle.id
    ORDER BY message_count DESC
    '''
    cursor.execute(query)
    print(f"{'ROWID':<8} {'Handle':<25} {'Messages':<8}")
    print('-' * 45)
    for row in cursor.fetchall():
        print(f"{row[0]:<8} {row[1]:<25} {row[2]:<8}")
    db.close()
else:
    print("Failed to connect to the database. Check permissions and path.") 