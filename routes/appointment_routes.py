from flask import Blueprint, request, jsonify
from services.ai_service import ai_service
from database import db
from models import Appointment, Staff, Notification
import uuid
from datetime import datetime

appointment_bp = Blueprint('appointments', __name__)

@appointment_bp.route('/slots', methods=['GET'])
def get_slots():
    date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    doctor_id = request.args.get('doctor')

    # Check workload and automatically set busy if > 5 appointments today
    from models import Staff, Appointment
    doctor = Staff.query.get(doctor_id) if doctor_id else None
    
    if doctor:
        today_count = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            db.func.date(Appointment.scheduled_at) == date
        ).count()
        
        if today_count >= 5:
            doctor.is_busy = True
            db.session.commit()
            
    is_busy = doctor.is_busy if doctor else False
    
    # Delegate to Agent 02 (Scheduler)
    agent_data = ai_service.get_appointment_slots(date, doctor_id)
    
    # Handle both list and dict responses
    if isinstance(agent_data, dict) and 'slots' in agent_data:
        slots_list = agent_data['slots']
    elif isinstance(agent_data, list):
        slots_list = agent_data
    else:
        slots_list = []

    # If agent is down or returns empty, provides default slots for demo
    if not slots_list:
        slots = [
            {"time": "09:00", "available": True},
            {"time": "10:00", "available": False},
            {"time": "11:00", "available": True},
            {"time": "14:00", "available": True},
            {"time": "15:00", "available": True},
        ]
    else:
        # Convert simple string slots (if any) to objects
        slots = []
        for s in slots_list:
            if isinstance(s, str):
                # Extract time part if it's ISO string
                time_part = s.split('T')[-1][:5] if 'T' in s else s
                slots.append({"time": time_part, "available": True})
            else:
                slots.append(s)
        
    # If doctor is busy, all slots are taken
    if is_busy:
        for s in slots:
            s['available'] = False
            
    return jsonify(slots), 200

@appointment_bp.route('/book', methods=['POST'])
def book_appointment():
    data = request.json
    # Expected: {patient_id, doctor_id, date, time, reason}
    
    # 1. Ask Agent 02 to validate and schedule
    agent_resp = ai_service.schedule_appointment(data)
    
    if "error" in agent_resp:
        return jsonify({"error": agent_resp["error"]}), 400
        
    # 2. Record in local database
    try:
        # Check for existing appointment at same time for this doctor OR same patient
        scheduled_at = datetime.strptime(f"{data.get('date')} {data.get('time')}", "%Y-%m-%d %H:%M")
        
        # Check if doctor is already busy at this exact time
        conflicting_doc = Appointment.query.filter(
            (Appointment.doctor_id == data.get('doctor_id')) & 
            (Appointment.scheduled_at == scheduled_at)
        ).first()
        
        if conflicting_doc:
            return jsonify({"error": "This time slot is no longer available for this doctor."}), 400
            
        # Check if patient is already booked elsewhere at this time
        conflicting_patient = Appointment.query.filter(
            (Appointment.patient_id == data.get('patient_id')) & 
            (Appointment.scheduled_at == scheduled_at)
        ).first()
        
        if conflicting_patient:
            return jsonify({"error": "You already have an appointment scheduled for this time."}), 400

        consultation_fee = 500.00
        print(f"DEBUG: Booking request received for patient {data.get('patient_id')} with doctor {data.get('doctor_id')}")
        new_appt = Appointment(
            id=str(uuid.uuid4()),
            patient_id=data.get('patient_id'),
            doctor_id=data.get('doctor_id'),
            triage_id=data.get('triage_id'),
            scheduled_at=datetime.strptime(f"{data.get('date')} {data.get('time')}", "%Y-%m-%d %H:%M"),
            status='scheduled',
            payment_status='pending',
            payment_amount=consultation_fee,
            payment_method='UPI',
            notes=data.get('reason', 'Portal Booking')
        )

        db.session.add(new_appt)
        db.session.commit()
        print(f"DEBUG: Successfully saved appointment {new_appt.id} — awaiting payment")
        
        return jsonify({
            "message": "Appointment booked — awaiting payment",
            "appointment_id": new_appt.id,
            "payment_amount": float(consultation_fee),
            "payment_status": "pending",
            "upi_id": "clinicai@ybl",
            "agent_confirmation": agent_resp.get("confirmation_code") or f"CONF-{uuid.uuid4().hex[:6].upper()}"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"DEBUG: ERROR SAVING APPOINTMENT: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Database save failed: {str(e)}"}), 500

@appointment_bp.route('/booked', methods=['GET'])
def get_booked_slots():
    date_str = request.args.get('date')
    doctor_id = request.args.get('doctor')
    
    if not date_str or not doctor_id:
        return jsonify([]), 200
        
    # Query appointments for this doctor on this day
    # We look for matches in the scheduled_at timestamp
    booked = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        db.func.date(Appointment.scheduled_at) == date_str # Assuming SQLite or similar
    ).all()
    
    return jsonify([b.scheduled_at.strftime("%H:%M") for b in booked if b.status != 'cancelled']), 200
    
@appointment_bp.route('/<appointment_id>/cancel', methods=['PUT', 'POST'])
def cancel_appointment(appointment_id: str):
    """Cancel an existing appointment."""
    appt = Appointment.query.get(appointment_id)
    if not appt:
        # Check by string ID just in case
        appt = Appointment.query.filter_by(id=appointment_id).first()
        
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404
        
    try:
        appt.status = 'cancelled'
        
        # Add Cancellation Notification
        notif = Notification(
            patient_id=appt.patient_id,
            channel='in_app',
            event_type='Appointment',
            subject='Appointment Cancelled',
            body=f"Your appointment with Dr. {Staff.query.get(appt.doctor_id).first_name if Staff.query.get(appt.doctor_id) else 'Specialist'} has been cancelled.",
            status='delivered'
        )
        db.session.add(notif)
        db.session.commit()
        
        return jsonify({"status": "cancelled", "message": "Appointment has been successfully removed from your schedule."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({\"error\": str(e)}), 500

@appointment_bp.route('/<appointment_id>/confirm-payment', methods=['POST'])
def confirm_payment(appointment_id: str):
    """Confirm UPI payment for an appointment."""
    appt = Appointment.query.get(appointment_id)
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404

    data = request.json or {}
    txn_id = data.get('txn_id', '').strip()

    if not txn_id:
        return jsonify({"error": "Transaction ID is required"}), 400

    try:
        appt.payment_status = 'paid'
        appt.payment_txn_id = txn_id
        appt.payment_method = data.get('method', 'UPI')
        appt.paid_at = datetime.utcnow()
        appt.status = 'confirmed'

        # Add payment confirmation notification
        notif = Notification(
            patient_id=appt.patient_id,
            channel='in_app',
            event_type='Payment',
            subject='Payment Confirmed',
            body=f"Payment of ₹{appt.payment_amount} received (Txn: {txn_id}). Your appointment is now confirmed.",
            status='delivered'
        )
        db.session.add(notif)
        db.session.commit()

        # Build receipt data
        doctor = Staff.query.get(appt.doctor_id)
        receipt = {
            "receipt_id": f"RCP-{uuid.uuid4().hex[:8].upper()}",
            "appointment_id": appt.id,
            "patient_id": appt.patient_id,
            "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Specialist",
            "doctor_specialty": doctor.speciality if doctor else "General Medicine",
            "scheduled_at": appt.scheduled_at.isoformat(),
            "date": appt.scheduled_at.strftime("%Y-%m-%d"),
            "time": appt.scheduled_at.strftime("%H:%M"),
            "amount": float(appt.payment_amount),
            "txn_id": txn_id,
            "payment_method": appt.payment_method,
            "paid_at": appt.paid_at.isoformat(),
            "status": "confirmed",
            "clinic_name": "CliniAI Medical Center",
            "clinic_address": "123 Health Avenue, Medical District",
            "clinic_phone": "+91-9876543210",
        }

        return jsonify({"message": "Payment confirmed", "receipt": receipt}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@appointment_bp.route('/<appointment_id>/receipt', methods=['GET'])
def get_receipt(appointment_id: str):
    """Get receipt for a paid appointment."""
    appt = Appointment.query.get(appointment_id)
    if not appt:
        return jsonify({"error": "Appointment not found"}), 404
    if appt.payment_status != 'paid':
        return jsonify({"error": "Payment not completed"}), 400

    doctor = Staff.query.get(appt.doctor_id)
    return jsonify({
        "receipt_id": f"RCP-{appt.id[:8].upper()}",
        "appointment_id": appt.id,
        "patient_id": appt.patient_id,
        "doctor_name": f"Dr. {doctor.first_name} {doctor.last_name}" if doctor else "Specialist",
        "doctor_specialty": doctor.speciality if doctor else "General Medicine",
        "date": appt.scheduled_at.strftime("%Y-%m-%d"),
        "time": appt.scheduled_at.strftime("%H:%M"),
        "amount": float(appt.payment_amount),
        "txn_id": appt.payment_txn_id,
        "payment_method": appt.payment_method,
        "paid_at": appt.paid_at.isoformat() if appt.paid_at else None,
        "status": appt.status,
        "clinic_name": "CliniAI Medical Center",
    }), 200
