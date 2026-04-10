import sys
import os

# Add the current directory to path
sys.path.append(os.getcwd())

try:
    from app import create_app
    from database import db
    from models.patient import Patient
    from datetime import date
    import uuid

    app, _ = create_app()
    with app.app_context():
        # Check if we already have patients
        if db.session.query(Patient).count() == 0:
            print("Seeding sample patient data...")
            p1 = Patient(
                id=str(uuid.uuid4()),
                first_name="John",
                last_name="Doe",
                dob=date(1985, 5, 20),
                gender="Male"
            )
            p2 = Patient(
                id=str(uuid.uuid4()),
                first_name="Jane",
                last_name="Smith",
                dob=date(1992, 8, 12),
                gender="Female"
            )
            db.session.add(p1)
            db.session.add(p2)
            db.session.commit()
            print("SUCCESS: Seeded 2 patients. Try searching for 'John' or 'Jane'.")
        else:
            print(f"DATABASE_STATUS: {db.session.query(Patient).count()} patients exist.")
            sample = db.session.query(Patient).first()
            print(f"HINT: Try searching for '{sample.first_name}'")
except Exception as e:
    print(f"ERROR: {str(e)}")
