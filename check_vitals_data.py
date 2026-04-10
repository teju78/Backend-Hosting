import pymysql, os
import sys
sys.path.append('e:/ClinicAI/backend')
from dotenv import load_dotenv
load_dotenv('e:/ClinicAI/backend/.env')

try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST','127.0.0.1'),
        user=os.getenv('DB_USER','root'),
        password=os.getenv('DB_PASSWORD',''),
        database=os.getenv('DB_NAME','mediagents_db'),
        port=int(os.getenv('DB_PORT',3306))
    )
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute('SELECT * FROM patient_vitals ORDER BY measured_at DESC LIMIT 5')
    rows = c.fetchall()
    print("Vitals data:")
    for r in rows:
        print(r)
    conn.close()
except Exception as e:
    print(f"Error: {e}")
