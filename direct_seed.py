import pymysql
import os
import uuid
from datetime import datetime, timedelta
from dotenv import load_dotenv
from cryptography.fernet import Fernet

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

def seed():
    patient_id = "7df841eb-089f-4cda-ba13-1017787f2643"
    print(f"Direct seeding for {patient_id}...")
    
    # Standard Clinical Key
    key = b'ONmBNnKyRqnbbm85R8K60XlSjpbSn7KYNhw27dQgE9M='
    cipher = Fernet(key)

    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            # 0. Update Patient Identifiers
            cursor.execute("""
                UPDATE patients 
                SET first_name_enc = %s, last_name_enc = %s, dob_enc = %s, blood_group = 'O+'
                WHERE id = %s
            """, (cipher.encrypt(b"Eswar"), cipher.encrypt(b"Ch"), cipher.encrypt(b"1998-05-15"), patient_id))

            now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
            # 1. Vitals
            cursor.execute("""
                INSERT INTO patient_vitals (id, patient_id, hr, bp_sys, bp_dia, spo2, temp_c, rr, glucose, measured_at)
                VALUES (%s, %s, 78, 120, 80, 98, 36.6, 16, 95, %s)
                ON DUPLICATE KEY UPDATE measured_at = %s
            """, (str(uuid.uuid4()), patient_id, now_str, now_str))
            
            # 2. Lab results
            cursor.execute("DELETE FROM lab_orders WHERE patient_id = %s", (patient_id,))
            cursor.execute("""
                INSERT INTO lab_orders (id, patient_id, test_name, status, resulted_at, created_at)
                VALUES (%s, %s, 'Full Blood Count', 'resulted', %s, %s)
            """, (str(uuid.uuid4()), patient_id, now_str, now_str))
            
            cursor.execute("""
                INSERT INTO lab_orders (id, patient_id, test_name, status, resulted_at, created_at)
                VALUES (%s, %s, 'Lipid Panel', 'resulted', %s, %s)
            """, (str(uuid.uuid4()), patient_id, now_str, now_str))
            
            conn.commit()
            print("Direct seeding complete.")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed()
