from flask import Blueprint, request, jsonify, current_app
from database import db
from models import Patient
from services.ai_service import ai_service
import jwt
import os

patient_bp = Blueprint('patients', __name__)

@patient_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    # Extract patient_id from token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        patient_id = decoded.get('user_id') # In this system, user_id and patient_id are often synced or linked
        # Better: get the actual patient_id if it's different
        from models import User
        user = User.query.get(patient_id)
        if user and user.patient_id:
            patient_id = user.patient_id
    except:
        return jsonify({"error": "Invalid token"}), 401

    if not patient_id:
        return jsonify({"error": "Patient context missing"}), 400

    # Parallel aggregation would be better, but serial for now
    ehr_record = ai_service.get_patient_context(patient_id)
    summary_data = ai_service.get_patient_summary(patient_id) # Using the summary method
    medications_report = ai_service.get_medications(patient_id)
    # Merged Appointments Logic
    raw_agent_appts = ai_service.get_appointments(patient_id)
    agent_appointments = []
    if isinstance(raw_agent_appts, list):
        for aa in raw_agent_appts:
            dt_str = aa.get('date') or aa.get('slot') or "2026-03-20T10:00:00Z"
            agent_appointments.append({
                "id": aa.get('id') or aa.get('appointment_id'),
                "doctor": aa.get('doctor_name') or aa.get('doctor'),
                "status": aa.get('status', 'Scheduled'),
                "date": dt_str.split('T')[0]
            })
    
    from models import Appointment, Staff
    local_appts = Appointment.query.filter_by(patient_id=patient_id).all()
    formatted_local = []
    for a in local_appts:
        doc = Staff.query.get(a.doctor_id)
        formatted_local.append({
            "id": a.id, "doctor": f"Dr. {doc.first_name if doc else 'Unknown'}", 
            "status": a.status, "date": a.scheduled_at.strftime("%Y-%m-%d")
        })
    appointments = formatted_local + agent_appointments
    risk_data = ai_service.get_risk_assessment(patient_id)

    # Calculate health score from risk (Risk 0-10, Health 0-100)
    # Higher risk = lower health
    risk_score = risk_data.get('risk_score', 1.0)
    calculated_health_score = int((10 - risk_score) * 10)

    # Transform EHR Vitals/Labs for Frontend
    vitals = {}
    if ehr_record.get('lab_results'):
        for lab in ehr_record['lab_results']:
            # Mock vitals if they are in labs for this demo
            if lab['test_name'] in ['Glucose', 'Creatinine', 'BP', 'Pulse']:
                vitals[lab['test_name']] = f"{lab['value']} {lab['unit']}"

    documents = []
    if ehr_record.get('lab_results'):
        for lab in ehr_record['lab_results']:
            documents.append({
                "name": f"{lab['test_name']} Result",
                "date": lab['date']
            })

    return jsonify({
        "summary": summary_data.get("summary_text", "No recent health alerts."),
        "vitals": vitals if vitals else {"Status": "Synchronized"},
        "medications": medications_report.get("medications", []),
        "appointments": appointments,
        "documents": documents[:3], # Limit to recent
        "health_score": calculated_health_score
    }), 200

@patient_bp.route('/medications', methods=['GET'])
def get_patient_medications():
    # Similar token auth logic as dashboard, but simplified for brevity here
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User
        user = User.query.get(user_id)
        patient_id = user.patient_id if user else None
    except:
        return jsonify({"error": "Invalid token"}), 401

    if not patient_id:
        return jsonify({"error": "Patient not found"}), 404

    report = ai_service.get_medications(patient_id)
    return jsonify(report), 200

@patient_bp.route('/medications/log', methods=['POST'])
def log_medication_dose():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User
        user = User.query.get(user_id)
        patient_id = user.patient_id if user else None
    except:
        return jsonify({"error": "Invalid token"}), 401

    if not patient_id:
        return jsonify({"error": "Patient not found"}), 404

    data = request.json
    drug_code = data.get('drug_code')
    status = data.get('status', 'Taken')
    
    if not drug_code:
        return jsonify({"error": "drug_code is required"}), 400

    result = ai_service.log_medication_dose(patient_id, drug_code, status)
    return jsonify(result), 200

@patient_bp.route('/medications/refill', methods=['POST'])
def request_medication_refill():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User
        user = User.query.get(user_id)
        patient_id = user.patient_id if user else None
    except:
        return jsonify({"error": "Invalid token"}), 401

    if not patient_id:
        return jsonify({"error": "Patient not found"}), 404

    data = request.json
    drug_name = data.get('drug_name')
    
    if not drug_name:
        return jsonify({"error": "drug_name is required"}), 400

    result = ai_service.request_medication_refill(patient_id, drug_name)
    
    # Save to local DB for history tracking + Create Notification
    try:
        from models import RefillRequest, Notification
        from database import db
        new_refill = RefillRequest(
            patient_id=patient_id,
            drug_name=drug_name,
            status='pending',
            notes="Automated request"
        )
        # Add notification
        notif = Notification(
            patient_id=patient_id,
            channel='in_app',
            event_type='Pharmacy',
            subject='Refill Request Logged',
            body=f"Your request for {drug_name} has been received and is pending clinical review.",
            status='delivered'
        )
        db.session.add(new_refill)
        db.session.add(notif)
        db.session.commit()
    except Exception as e:
        print(f"Error logging refill history: {e}")
        db.session.rollback()

    return jsonify(result), 200

@patient_bp.route('/medications/refill/history', methods=['GET'])
def get_refill_history():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User, RefillRequest
        user = User.query.get(user_id)
        patient_id = user.patient_id if user else None
        
        if not patient_id:
            return jsonify({"error": "Patient not found"}), 404

        history = RefillRequest.query.filter_by(patient_id=patient_id).order_by(RefillRequest.requested_at.desc()).all()
        return jsonify([{
            "id": h.id,
            "drug_name": h.drug_name,
            "status": h.status,
            "requested_at": h.requested_at.isoformat(),
            "processed_at": h.processed_at.isoformat() if h.processed_at else None,
            "notes": h.notes
        } for h in history]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@patient_bp.route('/appointments', methods=['GET'])
def get_patient_appointments():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User
        user = User.query.get(user_id)
        patient_id = user.patient_id if user else None
    except:
        return jsonify({"error": "Invalid token"}), 401

    if not patient_id:
        return jsonify({"error": "Patient not found"}), 404

    # 1. Get from Agent 02 and Normalize
    raw_agent_appts = ai_service.get_appointments(patient_id)
    agent_appointments = []
    if isinstance(raw_agent_appts, list):
        for aa in raw_agent_appts:
            # Normalize agent fields to match frontend expectation
            dt_str = aa.get('date') or aa.get('slot') or "2026-03-20T10:00:00Z"
            date_part = dt_str.split('T')[0]
            time_part = dt_str.split('T')[1][:5] if 'T' in dt_str else "10:00"
            
            agent_appointments.append({
                "id": aa.get('id') or aa.get('appointment_id'),
                "doctor": aa.get('doctor_name') or aa.get('doctor'),
                "specialty": aa.get('specialty') or "Specialist",
                "date": date_part,
                "time": time_part,
                "status": aa.get('status', 'Scheduled'),
                "type": aa.get('type', 'Consultation'),
                "location": aa.get('location', 'Virtual Clinic')
            })
        
    # 2. Get from Local DB
    from models import Appointment, Staff
    local_appts = Appointment.query.filter_by(patient_id=patient_id).all()
    
    formatted_local = []
    for a in local_appts:
        doctor = Staff.query.get(a.doctor_id)
        formatted_local.append({
            "id": a.id,
            "doctor": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Unknown Doctor",
            "specialty": doctor.speciality if doctor else "General Practice",
            "date": a.scheduled_at.strftime("%Y-%m-%d"),
            "time": a.scheduled_at.strftime("%H:%M"),
            "status": a.status,
            "type": "In-Person" if not a.room_id else "Video Consult",
            "location": "Main Medical Plaza" if not a.room_id else "Virtual Room",
            "doctor_is_busy": doctor.is_busy if doctor else False
        })

    # Add busy status to agent appointments if possible
    for aa in agent_appointments:
        # Simple name match for demo
        d_name = aa['doctor'].replace('Dr. ', '')
        doc = Staff.query.filter(Staff.first_name.contains(d_name) | Staff.last_name.contains(d_name)).first()
        aa['doctor_is_busy'] = doc.is_busy if doc else False

    # Combine
    return jsonify(formatted_local + agent_appointments), 200

@patient_bp.route('/', methods=['GET'])
def get_patients():
    patients = Patient.query.all()
    return jsonify([{
        "id": p.id,
        "mrn": p.mrn,
        "gender": p.gender,
        "blood_group": p.blood_group
    } for p in patients]), 200

@patient_bp.route('/<id>', methods=['GET'])
def get_patient(id):
    patient = Patient.query.get(id)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify({
        "id": patient.id,
        "mrn": patient.mrn,
        "gender": patient.gender,
        "blood_group": patient.blood_group
    }), 200

@patient_bp.route('/medications/add', methods=['POST'])
def add_patient_medication_manual():
    """Manual medication entry by patient."""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        
        from database import db
        from models import User, Prescription
        
        user = User.query.get(user_id)
        patient_id = user.patient_id if user else user_id
        data = request.get_json()
        
        if not data or not data.get('drug_name'):
            return jsonify({"error": "Drug name is required"}), 400
        
        
        from datetime import datetime
        
        new_med = Prescription(
            patient_id=patient_id,
            drug_name=data.get('drug_name'),
            drug_code=data.get('drug_code', data.get('drug_name')[:5].upper()),
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            route=data.get('route', 'Oral'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            refill_due_date=datetime.strptime(data['refill_due_date'], '%Y-%m-%d').date() if data.get('refill_due_date') else None,
            status='active',
            adherence_score=100.00,
            notes=data.get('notes', "Manually added by patient")
        )
        db.session.add(new_med)
        db.session.commit()
        return jsonify({"message": "Medication added successfully", "id": new_med.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
@patient_bp.route('/profile', methods=['GET'])
def get_patient_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        # Match secret key from app.py config fallback
        secret = current_app.config['SECRET_KEY']
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User
        user = User.query.get(user_id)
        if not user or not user.patient_id:
            return jsonify({"error": "Patient context not found"}), 404
        
        patient = Patient.query.get(user.patient_id)
        if not patient:
            return jsonify({"error": "Patient data not found"}), 404
            
        from routes.clinical_routes import _decrypt_pii

        return jsonify({
            "first_name": _decrypt_pii(patient.first_name_enc) or "",
            "last_name": _decrypt_pii(patient.last_name_enc) or "",
            "email": user.email,
            "dob": _decrypt_pii(patient.dob_enc) or "",
            "gender": str(_decrypt_pii(patient.gender) or patient.gender or "unknown"),
            "blood_group": str(_decrypt_pii(patient.blood_group) or patient.blood_group or ""),
            "height": str(_decrypt_pii(patient.height) or patient.height or ""),
            "weight": str(_decrypt_pii(patient.weight) or patient.weight or ""),
            "language_pref": str(_decrypt_pii(patient.language_pref) or patient.language_pref or "en"),
            "phone": _decrypt_pii(patient.phone_enc) or "",
            "preferences": {
                "health_updates": bool(patient.pref_health_updates),
                "appointments": bool(patient.pref_appointments),
                "medication": bool(patient.pref_medication)
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch profile: " + str(e)}), 500

@patient_bp.route('/profile', methods=['PUT'])
def update_patient_profile():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        # Match secret key from app.py config fallback
        secret = current_app.config['SECRET_KEY']
        decoded = jwt.decode(token, secret, algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User
        user = User.query.get(user_id)
        if not user or not user.patient_id:
            return jsonify({"error": "Patient context not found"}), 404
        
        patient = Patient.query.get(user.patient_id)
        data = request.json
        
        from cryptography.fernet import Fernet
        key = b'ONmBNnKyRqnbbm85R8K60XlSjpbSn7KYNhw27dQgE9M='
        cipher = Fernet(key)

        # Update fields with encryption
        if 'first_name' in data and data['first_name'] is not None: 
            patient.first_name_enc = cipher.encrypt(str(data['first_name']).encode('utf-8'))
        if 'last_name' in data and data['last_name'] is not None:  
            patient.last_name_enc = cipher.encrypt(str(data['last_name']).encode('utf-8'))
        if 'blood_group' in data: patient.blood_group = data['blood_group']
        if 'height' in data:     patient.height = data['height']
        if 'weight' in data:     patient.weight = data['weight']
        if 'gender' in data:     patient.gender = data['gender']
        if 'language_pref' in data: patient.language_pref = data['language_pref']
        if 'phone' in data and data['phone'] is not None:      
            patient.phone_enc = cipher.encrypt(str(data['phone']).encode('utf-8'))
        if 'dob' in data and data['dob'] is not None:        
            patient.dob_enc = cipher.encrypt(str(data['dob']).encode('utf-8'))
        
        if 'preferences' in data:
            p = data['preferences']
            if 'health_updates' in p: patient.pref_health_updates = p['health_updates']
            if 'appointments' in p:   patient.pref_appointments = p['appointments']
            if 'medication' in p:     patient.pref_medication = p['medication']
            
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        import traceback
        err_detail = traceback.format_exc()
        print(f"Update Profile Error: {err_detail}")
        db.session.rollback()
        return jsonify({"error": f"Update failed: {str(e)}"}), 400

@patient_bp.route('/delete-account', methods=['DELETE'])
def delete_patient_account():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        from models import User
        user = User.query.get(user_id)
        if not user or not user.patient_id:
            return jsonify({"error": "Patient context not found"}), 404
        
        patient = Patient.query.get(user.patient_id)
        db.session.delete(user)
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({"message": "Account permanently deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 401
