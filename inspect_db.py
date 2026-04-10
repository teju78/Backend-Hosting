import pymysql
import os
from dotenv import load_dotenv

load_dotenv('e:/ClinicAI/backend/.env')

def check_columns():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'mediagents_db'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        with conn.cursor() as cursor:
            cursor.execute("DESCRIBE patient_vitals")
            cols = cursor.fetchall()
            print("COLUMNS IN patient_vitals:")
            for col in cols:
                print(col)
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_columns()
