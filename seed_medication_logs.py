import pymysql
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'mediagents_db'),
        charset='utf8mb4'
    )

def seed_logs():
    patient_id = '7df841eb-089f-4cda-ba13-1017787f2643'
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get prescriptions with dates
            cursor.execute("SELECT * FROM prescriptions WHERE patient_id = %s", (patient_id,))
            prescriptions = cursor.fetchall()
            
            for rx in prescriptions:
                start_date = rx.get('start_date')
                end_date = rx.get('end_date') or datetime.now().date()
                drug_code = rx.get('drug_code')
                
                if not start_date:
                    start_date = datetime.now().date() - timedelta(days=7) # Default to 1 week back
                
                if isinstance(start_date, datetime): start_date = start_date.date()
                if isinstance(end_date, datetime): end_date = end_date.date()
                
                # Cap at today
                today = datetime.now().date()
                effective_end = min(end_date, today)
                
                current = start_date
                while current <= effective_end:
                    # Check if already logged
                    cursor.execute("""
                        SELECT id FROM medication_doses 
                        WHERE patient_id = %s AND drug_code = %s AND DATE(created_at) = %s
                    """, (patient_id, drug_code, current))
                    
                    if not cursor.fetchone():
                        import uuid
                        dose_id = str(uuid.uuid4())
                        # Create timestamp for midday
                        timestamp = datetime.combine(current, datetime.min.time()) + timedelta(hours=12)
                        
                        cursor.execute("""
                            INSERT INTO medication_doses (id, patient_id, drug_code, status, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (dose_id, patient_id, drug_code, 'Taken', timestamp))
                        print(f"Logged {drug_code} for {current}")
                    
                    current += timedelta(days=1)
            
            conn.commit()
            print("Successfully seeded medication logs")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_logs()
