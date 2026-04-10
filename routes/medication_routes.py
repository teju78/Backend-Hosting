from flask import Blueprint, request, jsonify
from services.ai_service import ai_service
from database import db
from models import Prescription
import uuid

medication_bp = Blueprint('medications', __name__)

@medication_bp.route('/<patient_id>', methods=['GET'])
def get_medications(patient_id):
    """Agent 07: Pharmacy Node"""
    name = request.args.get('patient_name')
    data = ai_service.get_medications(patient_id, patient_name=name)
    return jsonify(data), 200

@medication_bp.route('/', methods=['POST'])
def prescribe():
    """Agent 07: Pharmacy Node"""
    data = request.json
    # data: {patient_id, doctor_id, drug_name, dosage, frequency, duration}
    
    agent_resp = ai_service.prescribe(data)
    
    if "error" in agent_resp:
        return jsonify({"error": agent_resp["error"]}), 500
        
    from datetime import datetime
    from models import Prescription, Staff, Patient, Appointment
    try:
        start_date = None
        if data.get('start_date'):
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            
        end_date = None
        if data.get('end_date'):
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        raw_patient_id = data.get('patient_id')
        req_doctor_id = data.get('doctor_id')
        
        # 1. Resolve actual Patient ID if an Appointment ID was passed
        actual_patient_id = raw_patient_id
        if raw_patient_id and raw_patient_id.startswith('AUTO-'):
            appt = Appointment.query.get(raw_patient_id)
            if appt:
                actual_patient_id = appt.patient_id
            else:
                return jsonify({"error": f"Appointment {raw_patient_id} not found"}), 404

        # 2. Verify Patient exists
        patient = Patient.query.get(actual_patient_id)
        if not patient:
            return jsonify({"error": f"Patient {actual_patient_id} not found"}), 404

        # 3. Ensure doctor_id exists in staff table to avoid FK violation
        doctor = Staff.query.get(req_doctor_id) if req_doctor_id else None
        if not doctor:
            # Try to resolve DR-101 (seeded) as ultimate fallback
            doctor = Staff.query.get("DR-101")
        
        new_prescription = Prescription(
            patient_id=actual_patient_id,
            doctor_id=doctor.id if doctor else None,
            drug_name=data.get('drug_name'),
            dosage=data.get('dosage'),
            frequency=data.get('frequency'),
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        db.session.add(new_prescription)
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "prescription_id": new_prescription.id,
            "agent_ref": agent_resp.get("id")
        }), 201
    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        print(f"Prescribe Error: {error_info}")
        db.session.rollback()
        return jsonify({"error": str(e), "detail": "Database Commit or Agent Link failed"}), 500

@medication_bp.route('/<px_id>', methods=['DELETE'])
def remove_prescription(px_id):
    """Delete a prescription by ID."""
    from models import Prescription
    p = Prescription.query.get(px_id)
    if not p:
        return jsonify({"error": "Prescription not found"}), 404
    
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Medication removed"}), 200
