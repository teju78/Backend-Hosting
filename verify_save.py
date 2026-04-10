from app import create_app
from database import db
from models import TriageRecord
import sys

app, _ = create_app()
with app.app_context():
    record = db.session.query(TriageRecord).order_by(TriageRecord.created_at.desc()).first()
    if record:
        print(f"ID: {record.id}")
        print(f"Patient ID: {record.patient_id}")
        print(f"Urgency: {record.urgency_tier}")
        print(f"Symptom: {record.symptom_text}")
    else:
        print("No records found.")
