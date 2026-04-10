from database import db
from models import Staff, Patient
import app

def fix():
    flask_app, socketio = app.create_app()
    with flask_app.app_context():
        # 1. Force DR-101
        d = Staff.query.get('DR-101')
        if not d:
            d = Staff(
                id='DR-101', 
                first_name='John', 
                last_name='Doe', 
                role='doctor', 
                speciality='General Medicine', 
                is_on_duty=True
            )
            db.session.add(d)
        
        # 2. Force Patient 7df8
        pid = '7df841eb-089f-4cda-ba13-1017787f2643'
        p = Patient.query.get(pid)
        if not p:
            p = Patient(
                id=pid,
                mrn='MRN-TEMP',
                first_name_enc=b"Sess",
                last_name_enc=b"User",
                gender="other"
            )
            db.session.add(p)
            
        db.session.commit()
        print("✅ DATABASE IDS ALIGNED (DR-101 & Current User)")

if __name__ == "__main__":
    fix()
