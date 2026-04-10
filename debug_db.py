from database import db
from models import Patient, TriageRecord, Appointment
from sqlalchemy import func, text
from datetime import datetime
from app import create_app

app, socketio = create_app()
with app.app_context():
    print("CHECKING PATIENTS...")
    print(db.session.query(Patient).count())
    print("CHECKING TRIAGE...")
    print(db.session.query(TriageRecord).count())
    print("CHECKING WAIT TIME...")
    try:
        # Using text() correctly instead of func.text()
        wait = db.session.query(
            func.avg(
                func.timestampdiff(text('MINUTE'), TriageRecord.created_at, Appointment.scheduled_at)
            )
        ).join(Appointment, TriageRecord.id == Appointment.triage_id).scalar()
        print(f"WAIT: {wait}")
    except Exception as e:
        print(f"WAIT ERROR: {e}")
