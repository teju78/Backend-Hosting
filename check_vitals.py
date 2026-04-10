import pymysql
import os
from dotenv import load_dotenv

# Load env from backend
load_dotenv('e:/ClinicAI/backend/.env')

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mediagents_db"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "charset": "utf8mb4"
}

def check():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM patient_vitals")
            rows = cursor.fetchall()
            print(f"TOTAL_VITALS={len(rows)}")
            for r in rows:
                print(f"PID={r[1]}") # Assuming patient_id is second column
    finally:
        conn.close()

if __name__ == "__main__":
    check()
