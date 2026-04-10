import os
print("Starting migration...")
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load ENV first
load_dotenv()

# Build URI manually to avoid full app/socketio initialization
db_user = os.getenv('DB_USER', 'root')
db_pass = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_NAME', 'mediagents_db')

uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
engine = create_engine(uri)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SHOW COLUMNS FROM staff LIKE 'is_busy'"))
        if result.rowcount == 0:
            conn.execute(text("ALTER TABLE staff ADD COLUMN is_busy BOOLEAN DEFAULT FALSE AFTER is_on_duty"))
            conn.commit()
            print("Column 'is_busy' added successfully!")
        else:
            print("Column 'is_busy' already exists.")
except Exception as e:
    print(f"Error during migration: {e}")
