from app import create_app
from database import db
from sqlalchemy import text
import sys

app, _ = create_app()
with app.app_context():
    try:
        # Check icd10_hints
        result = db.session.execute(text("SHOW COLUMNS FROM triage_records LIKE 'icd10_hints'"))
        if not result.fetchone():
            print("Adding icd10_hints...")
            db.session.execute(text("ALTER TABLE triage_records ADD COLUMN icd10_hints JSON"))
            db.session.commit()
        
        # Check drug_alerts
        result = db.session.execute(text("SHOW COLUMNS FROM triage_records LIKE 'drug_alerts'"))
        if not result.fetchone():
            print("Adding drug_alerts...")
            db.session.execute(text("ALTER TABLE triage_records ADD COLUMN drug_alerts JSON"))
            db.session.commit()
            
        print("Success")
    except Exception as e:
        print(f"Error updating database: {e}")
        db.session.rollback()
        sys.exit(1)
