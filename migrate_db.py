import sys
from app import create_app
from database import db
from sqlalchemy import text

app, _ = create_app()

with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(text("SHOW COLUMNS FROM triage_records LIKE 'risk_analysis'"))
        if not result.fetchone():
            db.session.execute(text("ALTER TABLE triage_records ADD COLUMN risk_analysis JSON;"))
            db.session.commit()
            print("Successfully added 'risk_analysis' column to 'triage_records' table in MySQL.")
        else:
            print("Column 'risk_analysis' already exists.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
