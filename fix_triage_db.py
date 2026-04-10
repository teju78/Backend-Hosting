import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def fix_triage_table():
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'mediagents_db')

    uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(uri)
    
    with engine.connect() as conn:
        print("🛠️ Adding missing columns to triage_records...")
        # Add medication_analysis
        try:
            conn.execute(text("ALTER TABLE triage_records ADD COLUMN medication_analysis JSON"))
            print("✅ Added medication_analysis column.")
        except Exception as e:
            print(f"ℹ️ medication_analysis column might already exist: {e}")

        # Add decision_support
        try:
            conn.execute(text("ALTER TABLE triage_records ADD COLUMN decision_support JSON"))
            print("✅ Added decision_support column.")
        except Exception as e:
            print(f"ℹ️ decision_support column might already exist: {e}")

        # Ensure committed
        conn.commit()
    print("🚀 Database Sync Complete.")

if __name__ == "__main__":
    print("🚀 Starting Database Fix Script...")
    try:
        fix_triage_table()
        print("✅ Success: Database schema is now synchronized.")
    except Exception as e:
        print(f"❌ Critical Failure: {e}")
        import traceback
        traceback.print_exc()
