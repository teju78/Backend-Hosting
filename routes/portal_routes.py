"""
ClinicAI — Patient Portal Routes  /api/portal/*
================================================
Patient-facing portal: dashboard, medications, chat, triage history,
appointment bookings, and health score.
"""
from __future__ import annotations

import os
import jwt
from flask import Blueprint, request, jsonify, current_app
from database import db
from models import Patient, Appointment, Prescription, Notification, Staff
from services.ai_service import ai_service
from datetime import datetime, timezone

portal_bp = Blueprint("portal", __name__)


# ── Auth Helper ────────────────────────────────────────────────────────────────

def _get_patient_id() -> tuple[str | None, tuple | None]:
    """Extract and validate patient_id from JWT. Returns (patient_id, error)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    try:
        decoded    = jwt.decode(auth.split(" ")[1], current_app.config["SECRET_KEY"], algorithms=["HS256"])
        user_id    = decoded.get("user_id")
        from models import User
        user = User.query.get(user_id)
        patient_id = (user.patient_id if user else None) or user_id
        return patient_id, None
    except Exception:
        return None, (jsonify({"error": "Invalid token"}), 401)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@portal_bp.route("/dashboard", methods=["GET"])
def get_dashboard():
    """
    GET /api/portal/dashboard
    Full patient portal dashboard: health score, vitals, meds, appointments, alerts.
    Directly queries database for performance and reliability.
    """
    patient_id, err = _get_patient_id()
    if err:
        return err

    # Initialize all result variables
    health_score = 0
    risk_tier = "Stable"
    summary = "No recent health alerts."
    vitals = {}
    medications = []
    appointments = []
    documents = []
    insights = []
    patient_name = "Patient"
    patient_info = {}

    try:
        from sqlalchemy import text
        
        # 1. Latest Vitals from DB
        vitals_row = db.session.execute(text(
            "SELECT hr, bp_sys, bp_dia, spo2, temp_c, rr, glucose, measured_at FROM patient_vitals WHERE patient_id = :pid ORDER BY measured_at DESC LIMIT 1"
        ), {"pid": patient_id}).fetchone()
        
        if vitals_row:
            vitals = {
                "Heart Rate": f"{float(vitals_row.hr)} bpm" if vitals_row.hr else "N/A",
                "Systolic BP": f"{float(vitals_row.bp_sys)} mmHg" if vitals_row.bp_sys else "N/A",
                "Diastolic BP": f"{float(vitals_row.bp_dia)} mmHg" if vitals_row.bp_dia else "N/A",
                "Oxygen Saturation": f"{float(vitals_row.spo2)}%" if vitals_row.spo2 else "N/A",
                "Temperature": f"{float(vitals_row.temp_c)}°C" if vitals_row.temp_c else "N/A",
                "Respiratory Rate": f"{float(vitals_row.rr)} bpm" if vitals_row.rr else "N/A",
                "Glucose": f"{float(vitals_row.glucose)} mg/dL" if vitals_row.glucose else "N/A",
                "Recorded At": vitals_row.measured_at.strftime("%Y-%m-%d %H:%M") if vitals_row.measured_at else "N/A"
            }

        # 2. Risk Assessment from DB
        risk_row = db.session.execute(text(
            "SELECT deterioration_pct, risk_tier, recommended_intervention FROM risk_scores WHERE patient_id = :pid ORDER BY scored_at DESC LIMIT 1"
        ), {"pid": patient_id}).fetchone()
        
        if risk_row:
            det_risk = float(risk_row[0]) / 100.0 if risk_row[0] else 0.05
            risk_tier = risk_row[1] or "Stable"
            summary = risk_row[2] or "Health status synchronized from records."
            health_score = round(max(0.0, min(100.0, (1.0 - det_risk) * 100.0)))
        else:
            health_score = 100 # Default to healthy if no risk report
            summary = "Health status synchronized from records."

        # 3. Medications from DB
        meds_list = Prescription.query.filter_by(patient_id=patient_id, status='active').all()
        medications = [{
            "id": m.id,
            "name": m.drug_name,
            "dosage": m.dosage,
            "frequency": m.frequency,
            "route": m.route,
            "adherence_score": float(m.adherence_score) if m.adherence_score else 100.0,
            "status": m.status
        } for m in meds_list]

        # 4. Appointments from DB
        local_appts = Appointment.query.filter_by(patient_id=patient_id).order_by(
            Appointment.scheduled_at
        ).limit(5).all()
        
        for a in local_appts:
            doc = Staff.query.get(a.doctor_id)
            appointments.append({
                "id"           : a.id,
                "doctor_name"  : f"Dr. {doc.first_name} {doc.last_name}" if doc else "Specialist",
                "type"         : doc.speciality if doc else "General Medicine",
                "scheduled_at" : a.scheduled_at.isoformat(),
                "duration"     : a.duration_mins,
                "status"       : a.status,
                "priority"     : float(a.priority_score) if a.priority_score else None,
                "wait_mins"    : a.est_wait_mins,
                "notes"        : a.notes,
                "created_at"   : a.created_at.isoformat() if a.created_at else None
            })

        # 5. Documents/Health Records from DB
        # Lab results
        labs_rows = db.session.execute(text(
            "SELECT test_name, resulted_at FROM lab_orders WHERE patient_id = :pid AND status = 'resulted' ORDER BY resulted_at DESC LIMIT 3"
        ), {"pid": patient_id}).fetchall()
        
        for row in labs_rows:
            documents.append({
                "name": f"{row[0]} Result",
                "date": row[1].strftime("%Y-%m-%d") if row[1] else "Recent",
                "type": "Data"
            })

        # Triage Reports
        triage_rows = db.session.execute(text(
            "SELECT urgency_tier, created_at FROM triage_records WHERE patient_id = :pid ORDER BY created_at DESC LIMIT 2"
        ), {"pid": patient_id}).fetchall()
        
        for row in triage_rows:
            documents.append({
                "name": f"Clinical Triage Report: {row[0]}",
                "date": row[1].strftime("%Y-%m-%d") if row[1] else "Recent",
                "type": "Note"
            })

        # Insights from logic
        insights = []
        
        # Add vital summary if available
        vital_summary = ai_service.get_latest_vitals(patient_id).get("summary")
        if vital_summary:
            insights.append(f"Vitals Alert: {vital_summary}")
        
        insights.append(summary)
        
        if not medications:
            insights.append("No active medications on file.")
        if health_score < 70:
            insights.append("Recent data suggests increased monitoring may be needed.")

        # 6. Patient Profile details from DB
        patient = Patient.query.get(patient_id)
        if patient:
            patient_name = f"{patient.first_name} {patient.last_name}"
            patient_info = {
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "dob": patient.dob,
                "gender": patient.gender,
                "blood_group": patient.blood_group,
                "height": patient.height,
                "weight": patient.weight
            }

        # Notifications count
        unread_count = Notification.query.filter_by(patient_id=patient_id, read_at=None).count()

        return jsonify({
            "patient_id"      : patient_id,
            "patient_name"    : patient_name,
            "patient_info"    : patient_info,
            "health_score"    : health_score,
            "status"          : risk_tier,
            "vitals"          : vitals,
            "medications"     : medications,
            "appointments"    : appointments,
            "ai_insights"     : insights,
            "summary"         : summary,
            "documents"       : documents,
            "unread_notifs"   : unread_count,
            "generated_at"    : datetime.utcnow().isoformat(),
            "from_cache"      : False
        }), 200
        
    except Exception as e:
        print(f"Error in dashboard backend: {e}")
        return jsonify({"error": "Dashboard failed", "detail": str(e)}), 500


@portal_bp.route("/dashboard/advanced/<patient_id>", methods=["GET"])
def get_advanced_portal_dashboard(patient_id: str):
    """
    GET /api/portal/dashboard/advanced/{patient_id}
    Extended dashboard used by admin/doctor views.
    """
    ai_context = ai_service.get_patient_context(patient_id)
    med_report = ai_service.get_medications(patient_id)
    risk_data  = ai_service.get_risk_assessment(patient_id)

    health_score = ai_context.get("health_score", 84)
    status_label = ai_context.get("status_label", "Stable")

    med_list = med_report.get("medications", []) if not med_report.get("error") else []
    med_reminder = {
        "title"      : med_list[0]["name"] if med_list else "Check Medications",
        "instruction": med_list[0].get("dosage", "") if med_list else "No active reminders.",
        "icon"       : "HeartPulse",
    }

    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.scheduled_at
    ).limit(3).all()
    appt_data = [{
        "date"  : a.scheduled_at.strftime("%b %d"),
        "title" : a.notes or "General Consultation",
        "time"  : a.scheduled_at.strftime("%I:%M %p"),
        "status": a.status,
    } for a in appointments]

    return jsonify({
        "appointments": appt_data,
        "med_reminder": med_reminder,
        "health_score": health_score,
        "status"      : status_label,
        "ai_insights" : ai_context.get("insights", []),
        "risk"        : {
            "tier"             : risk_data.get("risk_tier", "Unknown"),
            "deterioration"    : risk_data.get("deterioration_risk", 0.0),
        } if not risk_data.get("error") else {},
    }), 200


# ── Symptom Check ─────────────────────────────────────────────────────────────

@portal_bp.route("/symptoms/check", methods=["POST"])
def check_symptoms():
    """
    POST /api/portal/symptoms/check
    Patient submits symptoms → instant triage via Agent 01.
    This is the lightweight version (no DB write); use /api/triage/submit for full pipeline.
    """
    patient_id, err = _get_patient_id()
    if err:
        return err

    data = request.json or {}
    result = ai_service.analyze_symptoms(
        patient_id = patient_id,
        symptoms   = data.get("symptoms", ""),
        severity   = data.get("severity", 5),
        duration   = data.get("duration", 1),
        age        = data.get("age", 35),
        sex        = data.get("sex", "Unknown"),
        conditions = data.get("conditions", []),
        medications= data.get("medications", []),
    )

    if result.get("error"):
        return jsonify({
            "error"            : True,
            "urgency_label"    : "Unknown",
            "urgency_tier"     : 3,
            "recommended_action": "Please contact the clinic directly.",
        }), 200  # Still 200 to show fallback UI

    return jsonify(result), 200


# ── Chat (Agent 08) ───────────────────────────────────────────────────────────

@portal_bp.route("/chat", methods=["POST"])
def chat_with_assistant():
    """POST /api/portal/chat — Chat with the AI Health Assistant (Agent 08)."""
    data       = request.json or {}
    patient_id = data.get("patient_id")
    message    = data.get("message") or data.get("content")
    session_id = data.get("session_id")

    if not patient_id:
        patient_id, err = _get_patient_id()
        if err:
            return err

    if not message:
        return jsonify({"error": "message is required"}), 400

    result = ai_service.chat_with_assistant(patient_id, message, session_id)
    if result.get("error"):
        return jsonify({
            "response_text"     : "I'm having trouble connecting right now. For urgent issues, call 999.",
            "intent"            : "Error",
            "escalation_required": False,
            "booking_suggested" : False,
            "session_id"        : session_id or "offline",
        }), 200

    return jsonify(result), 200


@portal_bp.route("/chat/history/<patient_id>", methods=["GET"])
def get_chat_history(patient_id: str):
    """GET /api/portal/chat/history/{patient_id} — Chat history from DB."""
    try:
        from models.chat import ChatMessage
        messages = ChatMessage.query.filter_by(patient_id=patient_id).order_by(
            ChatMessage.timestamp.asc(), ChatMessage.id.asc()
        ).all()
        return jsonify([m.to_dict() for m in messages]), 200
    except Exception:
        # If model doesn't exist yet, return empty
        return jsonify([]), 200


# ── Vitals & Monitoring ────────────────────────────────────────────────────────
@portal_bp.route("/vitals", methods=["GET"])
def get_my_vitals():
    """GET /api/portal/vitals — Patient's vital history + active alerts."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    # 1. Fetch history from Monitoring Agent
    history = ai_service.get_vitals_history(patient_id, limit=30)
    
    # 2. Fetch latest analysis (contains AI summary narrative)
    latest_analysis = ai_service.get_latest_vitals(patient_id)
    ai_summary = latest_analysis.get("summary") or "No recent vital analysis detected."
    
    # 3. Fetch active alerts
    alerts = ai_service.get_patient_alert(patient_id)
    
    # 4. Get DB history as fallback/backup
    from sqlalchemy import text
    try:
        db_history = db.session.execute(text(
            "SELECT hr, bp_sys, bp_dia, spo2, temp_c, rr, glucose, news2_score, measured_at FROM patient_vitals WHERE patient_id = :pid ORDER BY measured_at DESC LIMIT 10"
        ), {"pid": patient_id}).fetchall()
    except Exception:
        # Fallback if news2_score or glucose column is missing in older DB
        db_history = db.session.execute(text(
            "SELECT hr, bp_sys, bp_dia, spo2, temp_c, rr, measured_at FROM patient_vitals WHERE patient_id = :pid ORDER BY measured_at DESC LIMIT 10"
        ), {"pid": patient_id}).fetchall()
    
    db_readings = []
    for r in db_history:
        db_readings.append({
            "heart_rate": getattr(r, 'hr', None),
            "systolic_bp": getattr(r, 'bp_sys', None),
            "diastolic_bp": getattr(r, 'bp_dia', None),
            "spo2": getattr(r, 'spo2', None),
            "temperature": getattr(r, 'temp_c', None),
            "respiratory_rate": getattr(r, 'rr', None),
            "glucose": getattr(r, 'glucose', None) if hasattr(r, 'glucose') else None,
            "news2_score": getattr(r, 'news2_score', 0),
            "timestamp": getattr(r, 'measured_at', datetime.now()).isoformat() if getattr(r, 'measured_at', None) else None
        })

    # Clean up AI summary (remove LLM tokens)
    ai_summary = ai_summary.replace("</s>", "").replace("<s>", "").strip()

    return jsonify({
        "readings": db_readings,
        "alerts": alerts,
        "summary": ai_summary,
        "latest_analysis": latest_analysis
    }), 200

@portal_bp.route("/vitals", methods=["POST"])
def record_vitals():
    """POST /api/portal/vitals — Patient records their own vitals."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    data = request.json or {}
    # 1. Score via Monitoring Agent (Agent 03)
    # Agent 03 expected keys: heart_rate, temperature, respiratory_rate, spo2, systolic_bp, diastolic_bp, glucose
    score_res = ai_service.ingest_vitals(patient_id, {
        "heart_rate": float(data.get("heart_rate", 0)),
        "temperature": float(data.get("temperature", 0)),
        "respiration_rate": float(data.get("respiratory_rate", 0)),
        "sp_o2": float(data.get("spo2", 0)),
        "blood_pressure_sys": float(data.get("systolic_bp", 0)),
        "blood_pressure_dia": float(data.get("diastolic_bp", 0)),
        "blood_glucose": float(data.get("glucose", 0))
    })

    # 2. Persist to MySQL for long-term storage
    from sqlalchemy import text
    import uuid
    # Extract NEWS2 score from agent response
    n2s = score_res.get("news2_score", 0) if score_res else 0
    
    try:
        # Cast values to ensure they match DECIMAL types (5,2)
        params = {
            "id": str(uuid.uuid4()), "pid": patient_id, 
            "hr": float(data.get("heart_rate")) if data.get("heart_rate") not in [None, ""] else None,
            "bps": float(data.get("systolic_bp")) if data.get("systolic_bp") not in [None, ""] else None,
            "bpd": float(data.get("diastolic_bp")) if data.get("diastolic_bp") not in [None, ""] else None,
            "spo": float(data.get("spo2")) if data.get("spo2") not in [None, ""] else None,
            "tmp": float(data.get("temperature")) if data.get("temperature") not in [None, ""] else None,
            "rr": float(data.get("respiratory_rate")) if data.get("respiratory_rate") not in [None, ""] else None,
            "glu": float(data.get("glucose")) if data.get("glucose") not in [None, ""] else None,
            "n2s": n2s, "cat": datetime.now(timezone.utc)
        }
        db.session.execute(text("""
            INSERT INTO patient_vitals (id, patient_id, hr, bp_sys, bp_dia, spo2, temp_c, rr, glucose, news2_score, measured_at)
            VALUES (:id, :pid, :hr, :bps, :bpd, :spo, :tmp, :rr, :glu, :n2s, :cat)
        """), params)
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Failed standard INSERT into patient_vitals, falling back: {e}")
        db.session.rollback()
        # Fallback if news2_score or glucose columns are missing
        db.session.execute(text("""
            INSERT INTO patient_vitals (id, patient_id, hr, bp_sys, bp_dia, spo2, temp_c, rr, measured_at)
            VALUES (:id, :pid, :hr, :bps, :bpd, :spo, :tmp, :rr, :cat)
        """), {
            "id": str(uuid.uuid4()), "pid": patient_id, 
            "hr": data.get("heart_rate"), "bps": data.get("systolic_bp"), 
            "bpd": data.get("diastolic_bp"), "spo": data.get("spo2"), 
            "tmp": data.get("temperature"), "rr": data.get("respiratory_rate"), 
            "cat": datetime.now(timezone.utc)
        })
    db.session.commit()

    return jsonify({
        "success": True,
        "analysis": score_res,
        "message": "Vitals recorded and analyzed successfully."
    }), 201

# ── Health Record ─────────────────────────────────────────────────────────────

@portal_bp.route("/health-record", methods=["GET"])
def get_health_record():
    """GET /api/portal/health-record — Patient's EHR summary + vitals for portal."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    summary = ai_service.get_patient_summary(patient_id)
    vitals  = ai_service.get_latest_vitals(patient_id)
    risk    = ai_service.get_risk_assessment(patient_id)

    return jsonify({
        "summary" : summary if not summary.get("error") else {},
        "vitals"  : vitals  if not vitals.get("error")  else {},
        "risk"    : risk    if not risk.get("error")    else {},
    }), 200


# ── Medications ───────────────────────────────────────────────────────────────

@portal_bp.route("/medications", methods=["GET"])
def get_my_medications():
    """GET /api/portal/medications — Authenticated patient's medication list."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    result = ai_service.get_medications(patient_id)
    return jsonify(result if not result.get("error") else {"medications": []}), 200


# ── Appointments ──────────────────────────────────────────────────────────────

@portal_bp.route("/appointments", methods=["GET"])
def get_my_appointments():
    """GET /api/portal/appointments — Authenticated patient's upcoming appointments."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    local_appts = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.scheduled_at
    ).all()

    return jsonify([{
        "id"      : a.id,
        "doctor"  : f"Dr. {Staff.query.get(a.doctor_id).first_name}" if Staff.query.get(a.doctor_id) else "Specialist",
        "date"    : a.scheduled_at.strftime("%Y-%m-%d"),
        "time"    : a.scheduled_at.strftime("%H:%M"),
        "status"  : a.status,
        "notes"   : a.notes,
    } for a in local_appts]), 200


# ── Notifications ─────────────────────────────────────────────────────────────

@portal_bp.route("/notifications", methods=["GET"])
def get_notifications():
    """GET /api/portal/notifications — Patient's notifications."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    try:
        notifs = Notification.query.filter_by(patient_id=patient_id).order_by(
            Notification.created_at.desc()
        ).limit(50).all()
        return jsonify([{
            "id"        : n.id,
            "category"  : n.event_type or "System",
            "title"     : n.subject or "Notification",
            "desc"      : n.body or "",
            "isRead"    : n.read_at is not None,
            "created_at": n.created_at.isoformat() if n.created_at else None,
            "priority"  : "High" if n.event_type == "Emergency" else "Medium",
        } for n in notifs]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@portal_bp.route("/notifications/<notif_id>/read", methods=["PUT"])
def mark_notification_read(notif_id: str):
    """PUT /api/portal/notifications/{id}/read — Mark as read."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    notif = Notification.query.filter_by(id=notif_id, patient_id=patient_id).first()
    if not notif:
        return jsonify({"error": "Notification not found"}), 404

    notif.read_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"success": True}), 200


@portal_bp.route("/notifications/read-all", methods=["PUT"])
def mark_all_notifications_read():
    """PUT /api/portal/notifications/read-all — Mark all as read."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    Notification.query.filter_by(patient_id=patient_id, read_at=None).update(
        {Notification.read_at: datetime.utcnow()}, synchronize_session=False
    )
    db.session.commit()
    return jsonify({"success": True}), 200


@portal_bp.route("/notifications/<notif_id>", methods=["DELETE"])
def delete_notification(notif_id: str):
    """DELETE /api/portal/notifications/{id} — Dismiss notification."""
    patient_id, err = _get_patient_id()
    if err:
        return err

    notif = Notification.query.filter_by(id=notif_id, patient_id=patient_id).first()
    if not notif:
        return jsonify({"error": "Notification not found"}), 404

    db.session.delete(notif)
    db.session.commit()
    return jsonify({"success": True}), 200
