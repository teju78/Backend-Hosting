import pymysql
import os
from dotenv import load_dotenv

load_dotenv('e:/ClinicAI/backend/.env')

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mediagents_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def check_db_full():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            print("--- Users ---")
            cursor.execute("SELECT id, patient_id, role FROM users LIMIT 10")
            print(cursor.fetchall())
            print("\n--- Prescriptions ---")
            cursor.execute("SELECT * FROM prescriptions")
            print(cursor.fetchall())
    finally:
        conn.close()

if __name__ == "__main__":
    check_db_full()
