import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

db_user = os.getenv("DB_USER", "root")
db_pass = os.getenv("DB_PASSWORD", "")
db_host = os.getenv("DB_HOST", "localhost")
db_port = int(os.getenv("DB_PORT", "3306"))
db_name = os.getenv("DB_NAME", "mediagents_db")

try:
    conn = pymysql.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_pass,
        database=db_name
    )
    with conn.cursor() as cursor:
        print(f"Connecting to {db_name} at {db_host}")
        cursor.execute("SELECT COUNT(*) FROM alert_acknowledgments")
        count = cursor.fetchone()[0]
        print(f"Current rows in alert_acknowledgments: {count}")
        
    conn.close()
except Exception as e:
    print(f"Direct connection failure: {e}")
