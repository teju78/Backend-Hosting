import os
from app import create_app
from database import db
from models import Staff

app, _ = create_app()
with app.app_context():
    count = Staff.query.filter_by(role='doctor').count()
    print(f"Doctors count: {count}")
    if count == 0:
        print("No doctors found. Seeding a default doctor...")
        new_doc = Staff(
            first_name="Elena",
            last_name="Vance",
            role="doctor",
            speciality="Emergency Medicine",
            is_on_duty=True
        )
        db.session.add(new_doc)
        db.session.commit()
        print(f"Added default doctor: {new_doc.id}")
