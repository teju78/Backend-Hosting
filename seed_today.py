import sys
import os
import uuid
from datetime import datetime, timedelta

# Add e:\ClinicAI\backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models import Patient, Staff, Appointment, TriageRecord

def seed_today():
    app, _ = create_app()
    with app.app_context():
        # 1. Ensure Patient PAT-001 exists
        patient = Patient.query.get("PAT-001")
        if not patient:
            # We need to use b"encrypted" format since that's what the decryption expects
            # However, for demo, let's just make sure we have a few records
            patient = Patient(
                id="PAT-001",
                mrn="MRN-DEMO-01",
                first_name_enc=b"John",
                last_name_enc=b"Demo",
                dob_enc=b"1985-06-15",
                gender='male',
                blood_group="A+",
                language_pref="en"
            )
            db.session.add(patient)
            db.session.commit()
            print("Created patient PAT-001")

        # 2. Ensure Doctor DR-101 exists
        doctor = Staff.query.get("DR-101")
        if not doctor:
            doctor = Staff(
                id="DR-101",
                first_name="John",
                last_name="Doe",
                role="doctor",
                speciality="General Medicine",
                is_on_duty=True
            )
            db.session.add(doctor)
            db.session.commit()
            print("Created doctor DR-101")

        # 3. Create Triage Record (today)
        triage_id = f"TRIAGE-{str(uuid.uuid4())[:8]}"
        triage = TriageRecord(
            id=triage_id,
            patient_id="PAT-001",
            symptom_text="Persistent dry cough and high fever for 3 days",
            urgency_tier="Emergency", # Map to tier 1
            risk_analysis={"risk_score": 0.85, "reasoning": "High fever with respiratory symptoms"},
            decision_support={"differential_diagnosis": ["Pneumonia", "Influenza", "COVID-19"], "checklist": [{"task": "Chest X-Ray", "completed": False}]},
            created_at=datetime.utcnow()
        )
        db.session.add(triage)
        db.session.commit()
        print(f"Created triage record: {triage_id}")

        # 4. Create Appointment (Today)
        appt_id = f"AUTO-{str(uuid.uuid4())[:8]}"
        now = datetime.utcnow()
        appt = Appointment(
            id=appt_id,
            patient_id="PAT-001",
            doctor_id="DR-101",
            triage_id=triage_id,
            scheduled_at=now,
            status="scheduled",
            priority_score=0.9,
            notes="Demo Appointment - Urgent Case"
        )
        db.session.add(appt)
        db.session.commit()
        print(f"Created appointment: {appt_id}")

        # 5. Create Vitals (Now) - Using RAW SQL as there's no PatientVitals model
        v_id = str(uuid.uuid4())
        db.session.execute(db.text(
            """INSERT INTO patient_vitals (id, patient_id, hr, bp_sys, bp_dia, spo2, temp_c, rr, measured_at)
               VALUES (:id, :pid, :hr, :sys, :dia, :spo2, :temp, :rr, :at)"""
        ), {
            "id": v_id,
            "pid": "PAT-001",
            "hr": 102,
            "sys": 135,
            "dia": 88,
            "spo2": 94,
            "temp": 38.5,
            "rr": 20,
            "at": now
        })
        db.session.commit()
        print("Created vitals for PAT-001 (Raw SQL)")

        print(f"\n✅ DEMO DATA SEEDED")
        print(f"Patient ID: PAT-001")
        print(f"Appointment ID: {appt_id}")

if __name__ == "__main__":
    seed_today()
