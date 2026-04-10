import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 3306)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD') if os.getenv('DB_PASSWORD') else "",
            database=os.getenv('DB_NAME')
        )
        print("Successfully connected to MySQL database using PyMySQL")
        conn.close()
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")

if __name__ == "__main__":
    test_connection()
