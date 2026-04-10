import time
import json
import redis
import threading
from flask_socketio import SocketIO
from database import db
from models import TriageRecord

PROCESSED_IDS = set()

def start_redis_listener(socketio: SocketIO, app, redis_host='localhost', redis_port=6379):
    def listener():
        try:
            r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=2)
            # Test connection
            r.ping()
            streams = {
                'triage_result': '$',
                'appointment_scheduled': '$',
                'risk_score_updated': '$',
                'ehr_updated': '$',
                'clinical_synthesis': '$',
                'decision_ready': '$',
                'medication_ready': '$',
                'emergency_alert': '$',
                'orchestrator_update': '$',
            }
            
            print("Backend Redis Listener Started...")
            
            while True:
                try:
                    messages = r.xread(streams, block=1000)
                    if messages:
                        for stream, msg_list in messages:
                            for msg_id, payload in msg_list:
                                data = json.loads(payload['data'])
                                
                                # 🛡️ Atomic Deduplication check (Redis-based)
                                # Only process if we can set a lock for this event ID (expires in 60s)
                                event_id = data.get('triage_id') or data.get('patient_id') or msg_id
                                lock_key = f"processed:{stream}:{event_id}"
                                
                                # Always emit to SocketIO first so frontend stays in sync, even if 
                                # we deduplicate the database processing below.
                                try:
                                    socketio.emit('event_bus_message', {
                                        'stream': stream,
                                        'data': data
                                    })
                                except Exception as se:
                                    print(f"Error emitting to socket: {se}")

                                if not r.set(lock_key, "1", ex=60, nx=True):
                                    print(f"--- [DEDUP] Skipping duplicate database sync for: {lock_key} ---")
                                    continue
                                
                                print(f"--- [REDIS] {stream} INCOMING ---")
                                print(f"Payload: {data}")
                                
                                # Update database in background for agents
                                with app.app_context():
                                    triage_id = data.get('triage_id')
                                    patient_id = data.get('patient_id')
                                    
                                    # Fallback for appointment_scheduled payload structure
                                    if not patient_id and 'current_queue' in data:
                                        patient_id = data['current_queue'][0].get('patient_id')
                                    
                                    print(f"DEBUG: Looking for TriageRecord. triage_id={triage_id}, patient_id={patient_id}")
                                    
                                    # Try finding by triage_id first, then latest for patient.
                                    # Add 3-retry logic with small delay to handle race condition with initial save.
                                    record = None
                                    for attempt in range(3):
                                        if triage_id:
                                            record = TriageRecord.query.get(triage_id)
                                        if not record and patient_id:
                                            # If no record found by ID, try finding most recent for patient
                                            record = TriageRecord.query.filter_by(patient_id=patient_id).order_by(TriageRecord.created_at.desc()).first()
                                        
                                        if record:
                                            break
                                        if attempt < 2:
                                            print(f"⏳ Record not found yet, retrying sync ({attempt+1}/3)...")
                                            db.session.rollback() # Clear session to see new commits
                                            time.sleep(1.0)
                                        
                                    if record:
                                        print(f"DEBUG: Found TriageRecord ID={record.id} for sync.")
                                        if stream == 'triage_result':
                                            record.icd10_hints = data.get('icd10_hints', record.icd10_hints)
                                            record.drug_alerts = data.get('drug_alerts', record.drug_alerts)
                                            db.session.commit()
                                            print(f"✅ Sync'd triage details for {record.id}")
                                            
                                        elif stream == 'risk_score_updated':
                                            record.risk_analysis = data
                                            db.session.commit()
                                            print(f"✅ Sync'd risk analysis for {record.id}")

                                        elif stream == 'medication_ready':
                                            record.medication_analysis = data.get('medication_report', record.medication_analysis)
                                            db.session.commit()
                                            print(f"✅ Sync'd medication analysis for {record.id}")

                                        elif stream == 'decision_ready':
                                            record.decision_support = data
                                            db.session.commit()
                                            print(f"✅ Sync'd decision support for {record.id}")

                                        elif stream == 'appointment_scheduled':
                                            appt_info = None
                                            if data.get('appointment'):
                                                appt_info = data.get('appointment')
                                            elif data.get('current_queue'):
                                                appt_info = data.get('current_queue', [{}])[0]
                                                
                                            if appt_info:
                                                record.assigned_doctor = appt_info.get('doctor_name', record.assigned_doctor)
                                            
                                            # AUTO-COMMIT: Create actual appointment record
                                            from models import Appointment, Staff
                                            import uuid
                                            from datetime import datetime
                                            
                                            slot_str = appt_info.get('slot', '').replace('T', ' ')
                                            if slot_str and len(slot_str) > 16: 
                                                slot_str = slot_str[:16]
                                            
                                            doc_id = str(appt_info.get('doctor_id', 'DR-101'))
                                            
                                            # STRICT DEDUPLICATION
                                            existing = None
                                            if slot_str and record:
                                                try:
                                                    target_time = datetime.strptime(slot_str, "%Y-%m-%d %H:%M")
                                                    existing = Appointment.query.filter(
                                                        (Appointment.triage_id == str(record.id)) | 
                                                        ((Appointment.patient_id == str(record.patient_id)) & (Appointment.scheduled_at == target_time))
                                                    ).first()
                                                    
                                                    if not existing:
                                                        # Ensure doctor exists
                                                        active_doc = Staff.query.get(doc_id)
                                                        if not active_doc:
                                                            print(f"🛠️ Creating missing doctor: {doc_id}")
                                                            active_doc = Staff(
                                                                id=doc_id, role='doctor', 
                                                                first_name="Specialist", last_name="Physician",
                                                                is_on_duty=True
                                                            )
                                                            db.session.add(active_doc)
                                                            db.session.commit()
                                                        
                                                        new_appt = Appointment(
                                                            id=f"AUTO-{str(uuid.uuid4())[:8]}",
                                                            patient_id=str(record.patient_id),
                                                            doctor_id=doc_id, 
                                                            triage_id=str(record.id),
                                                            scheduled_at=target_time,
                                                            status='scheduled',
                                                            notes=f"AI Triage Auto-Booking (TID: {str(record.id)})"
                                                        )
                                                        db.session.add(new_appt)
                                                        db.session.commit()
                                                        print(f"🔥 AUTO-BOOKED appointment for Patient {record.patient_id}")
                                                    else:
                                                        print(f"ℹ️ Appointment already exists for record {record.id}")
                                                except Exception as e:
                                                    db.session.rollback()
                                                    print(f"⚠️ Auto-booking error: {e}")
                                            
                                            db.session.commit()
                                            print(f"✅ Sync'd record {record.id}")
                                    else:
                                        print(f"⚠️ NO RECORD FOUND for triage_id={triage_id}, patient_id={patient_id}")
                                
                except Exception as e:
                    print(f"Error in Redis listener: {e}")
                    time.sleep(1)
        except Exception as e:
            print(f"Redis not available - running without event bus: {e}")
            # Don't start the listener thread if Redis is not available
            return

    thread = threading.Thread(target=listener, daemon=True)
    thread.start()
