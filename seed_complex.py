from app import create_app
from database import db
from models import User, Patient, Staff
import bcrypt
import uuid
from datetime import datetime

def seed_all():
    app, socketio = create_app()
    with app.app_context():
        # 1. Create a Patient
        patient_id = "PAT-001"
        patient_obj = Patient.query.get(patient_id)
        if not patient_obj:
            patient_obj = Patient(
                id=patient_id,
                mrn="MRN-001",
                first_name_enc=b"Patient",
                last_name_enc=b"Test",
                dob_enc=b"1990-01-01",
                gender="male",
                blood_group="O+",
                language_pref="en",
                phone_enc=b"+1234567890",
                email_enc=b"patient@clinic.ai"
            )
            db.session.add(patient_obj)
            print(f"Created Patient {patient_id}")
        
        # 2. Create Staff (Doctor, Dentist, Admin)
        staff_data = [
            {"id": "DR-101", "email": "doctor@clinic.ai", "first": "John", "last": "Doe", "role": "doctor", "speciality": "General Medicine", "license": "LIC-DOC-001", "phone": "555-0101"},
            {"id": "DR-102", "email": "dentist@clinic.ai", "first": "Jane", "last": "Smooth", "role": "dentist", "speciality": "Orthodontics", "license": "LIC-DEN-001", "phone": "555-0102"},
            {"id": "ADM-001", "email": "admin@clinic.ai", "first": "System", "last": "Admin", "role": "admin", "speciality": "Systems", "license": "LIC-ADM-001", "phone": "555-0103"}
        ]
        
        staff_map = {}
        for s in staff_data:
            staff_obj = Staff.query.get(s['id'])
            if not staff_obj:
                staff_obj = Staff(
                    id=s['id'],
                    first_name=s['first'],
                    last_name=s['last'],
                    role=s['role'],
                    speciality=s['speciality'],
                    license_number=s['license'],
                    phone=s['phone'],
                    is_on_duty=True
                )
                db.session.add(staff_obj)
                print(f"Created Staff: {s['first']} {s['last']} ({s['role']})")
            else:
                staff_obj.is_on_duty = True
            staff_map[s['email']] = staff_obj

        # 3. Create Users and Link
        user_data = [
            {"id": "USR-001", "email": "patient@clinic.ai", "password": "password123", "role": "patient", "patient_id": patient_obj.id, "staff_id": None},
            {"id": "USR-002", "email": "doctor@clinic.ai", "password": "password123", "role": "doctor", "patient_id": None, "staff_id": staff_map["doctor@clinic.ai"].id},
            {"id": "USR-003", "email": "dentist@clinic.ai", "password": "password123", "role": "dentist", "patient_id": None, "staff_id": staff_map["dentist@clinic.ai"].id},
            {"id": "USR-004", "email": "admin@clinic.ai", "password": "password123", "role": "admin", "patient_id": None, "staff_id": staff_map["admin@clinic.ai"].id},
        ]

        for u in user_data:
            existing_user = User.query.get(u['id'])
            if not existing_user:
                hashed_pw = bcrypt.hashpw(u['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                new_user = User(
                    id=u['id'],
                    email=u['email'],
                    password_hash=hashed_pw,
                    role=u['role'],
                    patient_id=u['patient_id'],
                    staff_id=u['staff_id']
                )
                db.session.add(new_user)
                print(f"Created user: {u['email']} ({u['role']})")
        
        db.session.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    seed_all()
