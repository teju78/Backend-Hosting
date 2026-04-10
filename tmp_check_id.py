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

def check(identifier):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # Check patients
        cursor.execute("SELECT id, mrn FROM patients WHERE id = %s", (identifier,))
        p = cursor.fetchone()
        if p:
            print(f"FOUND IN PATIENTS: {p}")
        
        # Check appointments
        cursor.execute("SELECT id, patient_id FROM appointments WHERE id = %s", (identifier,))
        a = cursor.fetchone()
        if a:
            print(f"FOUND IN APPOINTMENTS: {a}")
            
        if not p and not a:
            print(f"NOT FOUND: {identifier}")
            
        conn.close()
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check(sys.argv[1])
    else:
        print("Usage: python check_id.py <identifier>")
