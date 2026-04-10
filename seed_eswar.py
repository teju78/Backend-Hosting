import sys
import os
import uuid
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

# Fix path to allow importing from parent
sys.path.append(os.path.dirname(os.getcwd()))

from app import create_app
from database import db
from models import Prescription, Appointment, Staff, Patient
from sqlalchemy import text

def seed_eswar():
    app, socketio = create_app()
    patient_id = "7df841eb-089f-4cda-ba13-1017787f2643"
    
    # Standard Clinical Key
    key = b'8-GP0vV7e_f8S-r9L1_6K-8P7J-V4R-2Q-1W-3E-4R='
    cipher = Fernet(key)

    with app.app_context():
        print(f"Seeding data for patient {patient_id}...")
        
        # 1. Ensure Patient exists
        patient = Patient.query.get(patient_id)
        if patient:
            db.session.delete(patient)
            db.session.commit()
            print("Refreshing existing patient...")

        patient = Patient(
            id=patient_id,
            mrn=f"MRN-{patient_id[:8].upper()}",
            first_name_enc=cipher.encrypt(b"Eswar"),
            last_name_enc=cipher.encrypt(b"Ch"),
            dob_enc=cipher.encrypt(b"1998-05-15"),
            gender="male",
            blood_group="O+"
        )
        db.session.add(patient)
        db.session.commit()

        # 2. Add some vitals
        db.session.execute(text("""
            INSERT INTO patient_vitals (id, patient_id, hr, bp_sys, bp_dia, spo2, temp_c, rr, glucose, measured_at)
            VALUES (:id, :pid, 78, 120, 80, 98, 36.6, 16, 95, :now)
        """), {
            "id": str(uuid.uuid4()),
            "pid": patient_id,
            "now": datetime.utcnow()
        })
        
        # 3. Add medications
        meds = [
            Prescription(id=str(uuid.uuid4()), patient_id=patient_id, drug_name="Lisinopril", dosage="10mg", frequency="Once daily", route="Oral", status="active", start_date=datetime.now().date()),
            Prescription(id=str(uuid.uuid4()), patient_id=patient_id, drug_name="Metformin", dosage="500mg", frequency="Twice daily", route="Oral", status="active", start_date=datetime.now().date() - timedelta(days=30))
        ]
        db.session.add_all(meds)
        
        db.session.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    seed_eswar()
