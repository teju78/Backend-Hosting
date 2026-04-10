import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv('DB_USER', 'root')
db_pass = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_name = os.getenv('DB_NAME', 'mediagents_db')

try:
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE chat_messages")
        print("Schema:", cursor.fetchall())
        
        cursor.execute("SELECT id, patient_id, role, content FROM chat_messages ORDER BY id ASC")
        print("Rows:", cursor.fetchall())
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
