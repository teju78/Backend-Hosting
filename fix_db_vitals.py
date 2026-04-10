import pymysql
import os
from dotenv import load_dotenv

# Use absolute path for .env
load_dotenv('e:/ClinicAI/backend/.env')

def fix_db():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'mediagents_db'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        with conn.cursor() as cursor:
            # Check if glucose column exists
            cursor.execute("SHOW COLUMNS FROM patient_vitals LIKE 'glucose'")
            if not cursor.fetchone():
                print("Adding glucose column...")
                cursor.execute("ALTER TABLE patient_vitals ADD COLUMN glucose DECIMAL(5,2) AFTER rr")
                conn.commit()
                print("Success!")
            else:
                print("Glucose column already exists.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()
