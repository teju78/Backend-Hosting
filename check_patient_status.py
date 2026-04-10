import os
import sys
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mediagents_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def check():
    pid = "7df841eb-089f-4cda-ba13-1017787f2643"
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT HEX(first_name_enc), blood_group FROM patients WHERE id = %s", (pid,))
        res = cursor.fetchone()
        if res:
            print(f"RESULT: HEX_NAME={res[0]} BLOOD={res[1]}")
        else:
            print("RESULT: NOT_FOUND")
        conn.close()
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    check()
