import sys
from app import create_app
from database import db
from sqlalchemy import text

app, _ = create_app()

def migrate():
    with app.app_context():
        try:
            # Check for glucose
            result = db.session.execute(text("SHOW COLUMNS FROM patient_vitals LIKE 'glucose'"))
            if not result.fetchone():
                print("Adding glucose column to patient_vitals...")
                db.session.execute(text("ALTER TABLE patient_vitals ADD COLUMN glucose DECIMAL(5,2);"))
                db.session.commit()
                print("Success")
            else:
                print("Glucose exists")

            # Check for news2_score
            result = db.session.execute(text("SHOW COLUMNS FROM patient_vitals LIKE 'news2_score'"))
            if not result.fetchone():
                print("Adding news2_score column to patient_vitals...")
                db.session.execute(text("ALTER TABLE patient_vitals ADD COLUMN news2_score INT DEFAULT 0;"))
                db.session.commit()
                print("Success")
            else:
                print("news2_score exists")

            # Check for news2_score in dashboard queries
            try:
                db.session.execute(text("SELECT news2_score FROM patient_vitals LIMIT 1"))
            except Exception as e:
                print(f"Warning: news2_score still not accessible: {e}")

        except Exception as e:
            print(f"Migration Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    migrate()
