import pymysql
import os
from dotenv import load_dotenv

# Use absolute path for .env
load_dotenv('e:/ClinicAI/backend/.env')

LOG_FILE = 'e:/ClinicAI/backend/migration_log.txt'

def migrate():
    with open(LOG_FILE, 'w') as log:
        log.write("Migration started\n")
        try:
            conn = pymysql.connect(
                host=os.getenv('DB_HOST', '127.0.0.1'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'mediagents_db'),
                port=int(os.getenv('DB_PORT', 3306))
            )
            log.write("Connected to DB\n")
            with conn.cursor() as cursor:
                # Add glucose
                try:
                    cursor.execute("ALTER TABLE patient_vitals ADD COLUMN glucose DECIMAL(5,2) AFTER rr")
                    conn.commit()
                    log.write("Added glucose column\n")
                except Exception as e:
                    log.write(f"Glucose column error/exists: {e}\n")
                
                # Add news2_score
                try:
                    cursor.execute("ALTER TABLE patient_vitals ADD COLUMN news2_score INT DEFAULT 0 AFTER glucose")
                    conn.commit()
                    log.write("Added news2_score column\n")
                except Exception as e:
                    log.write(f"news2_score column error/exists: {e}\n")
                    
            conn.close()
            log.write("Migration finished successfully\n")
        except Exception as e:
            log.write(f"Connection Error: {e}\n")

if __name__ == "__main__":
    migrate()
