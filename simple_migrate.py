import pymysql
import os
from dotenv import load_dotenv

# Use absolute path for .env
load_dotenv('e:/ClinicAI/backend/.env')

def migrate():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'mediagents_db'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        with conn.cursor() as cursor:
            # Add glucose
            try:
                cursor.execute("ALTER TABLE patient_vitals ADD COLUMN glucose DECIMAL(5,2) AFTER rr")
                conn.commit()
                print("Added glucose")
            except:
                print("Glucose already exists or failed")
            
            # Add news2_score
            try:
                cursor.execute("ALTER TABLE patient_vitals ADD COLUMN news2_score INT DEFAULT 0 AFTER glucose")
                conn.commit()
                print("Added news2_score")
            except:
                print("news2_score already exists or failed")
                
        conn.close()
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate()
