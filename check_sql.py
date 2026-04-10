import os
import pymysql
from dotenv import load_dotenv

load_dotenv()
db_user = os.getenv("DB_USER", "root")
db_pass = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", "3306"))
db_name = os.getenv("DB_NAME", "mediagents_db")

try:
    conn = pymysql.connect(
        host=db_host, user=db_user, password=db_pass, 
        database=db_name, port=db_port
    )
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES LIKE 'alert_acknowledgments'")
        result = cursor.fetchone()
        if result:
            print("Table alert_acknowledgments EXISTS.")
            cursor.execute("DESCRIBE alert_acknowledgments")
            for col in cursor.fetchall():
                print(col)
        else:
            print("Table alert_acknowledgments MISSING.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
