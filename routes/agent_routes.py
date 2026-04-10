"""
ClinicAI — Agent Proxy Routes  /api/agents/*
============================================
Direct proxy routes that let the frontend call any AI agent
through the backend (handles CORS, auth, logging, and error shaping).
"""
from flask import Blueprint, request, jsonify, current_app
from services.ai_service import ai_service
import jwt, os

agent_bp = Blueprint("agents", __name__)


def _get_patient_from_token():
    """Extract patient_id from JWT Bearer token. Returns (patient_id, error_response)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, (jsonify({"error": "Unauthorized"}), 401)
    try:
        decoded    = jwt.decode(auth.split(" ")[1], current_app.config["SECRET_KEY"], algorithms=["HS256"])
        patient_id = decoded.get("user_id")
        from models import User
        user = User.query.get(patient_id)
        if user and user.patient_id:
            patient_id = user.patient_id
        return patient_id, None
    except Exception:
        return None, (jsonify({"error": "Invalid token"}), 401)


# ── System ─────────────────────────────────────────────────────────────────────

@agent_bp.route("/health", methods=["GET"])
def agents_health():
    """Get real-time health status of all agents."""
    data = ai_service.get_agents_status()
    return jsonify(data), 200


@agent_bp.route("/health/<agent_name>", methods=["GET"])
def single_agent_health(agent_name: str):
    data = ai_service.check_agent(agent_name)
    return jsonify(data), 200


# ── Agent 01: Triage ──────────────────────────────────────────────────────────

@agent_bp.route("/triage", methods=["POST"])
def direct_triage():
    """Direct triage call to Agent 01 (bypasses DB for instant feedback)."""
    data       = request.json or {}
    patient_id = data.get("patient_id")
    symptoms   = data.get("symptoms") or data.get("symptom_text")
    if not symptoms:
        return jsonify({"error": "symptoms is required"}), 400

    result = ai_service.analyze_symptoms(
        patient_id = patient_id,
        symptoms   = symptoms,
        severity   = data.get("severity", 5),
        duration   = data.get("duration", 1),
        age        = data.get("age", 35),
        sex        = data.get("sex", "Unknown"),
        conditions = data.get("conditions", []),
        medications= data.get("medications", []),
    )
    status = 503 if result.get("error") else 200
    return jsonify(result), status


@agent_bp.route("/triage/<triage_id>", methods=["GET"])
def get_triage(triage_id: str):
    result = ai_service.get_triage_result(triage_id)
    return jsonify(result), 200


@agent_bp.route("/triage/status/<patient_id>", methods=["GET"])
def get_patient_triage(patient_id: str):
    result = ai_service.get_patient_triage_status(patient_id)
    return jsonify(result), 200


# ── Agent 03: Monitoring ──────────────────────────────────────────────────────

@agent_bp.route("/vitals/<patient_id>/ingest", methods=["POST"])
def ingest_vitals(patient_id: str):
    """Push a new vital reading to the monitoring agent."""
    data = request.json or {}
    result = ai_service.ingest_vitals(patient_id, data)
    status = 503 if result.get("error") else 200
    return jsonify(result), status


@agent_bp.route("/vitals/<patient_id>", methods=["GET"])
def get_vitals(patient_id: str):
    result = ai_service.get_latest_vitals(patient_id)
    return jsonify(result), 200


@agent_bp.route("/vitals/<patient_id>/history", methods=["GET"])
def get_vitals_history(patient_id: str):
    limit  = int(request.args.get("limit", 20))
    result = ai_service.get_vitals_history(patient_id, limit)
    return jsonify(result), 200


@agent_bp.route("/monitoring/alerts", methods=["GET"])
def get_monitoring_alerts():
    result = ai_service.get_all_alerts()
    return jsonify(result), 200


@agent_bp.route("/monitoring/alerts/<patient_id>", methods=["GET"])
def get_patient_monitoring_alert(patient_id: str):
    result = ai_service.get_patient_alert(patient_id)
    return jsonify(result), 200


# ── Agent 04: Risk ────────────────────────────────────────────────────────────

@agent_bp.route("/risk/<patient_id>", methods=["GET"])
def get_risk(patient_id: str):
    result = ai_service.get_risk_assessment(patient_id)
    return jsonify(result), 200


@agent_bp.route("/risk/<patient_id>/history", methods=["GET"])
def get_risk_history(patient_id: str):
    limit  = int(request.args.get("limit", 10))
    result = ai_service.get_risk_history(patient_id, limit)
    return jsonify(result), 200


@agent_bp.route("/risk/score", methods=["POST"])
def score_risk():
    data   = request.json or {}
    result = ai_service.score_risk(data)
    status = 503 if result.get("error") else 200
    return jsonify(result), status


# ── Agent 05: Decision Support ────────────────────────────────────────────────

@agent_bp.route("/decision/<patient_id>", methods=["GET"])
def get_decision(patient_id: str):
    result = ai_service.get_decision_support(patient_id)
    return jsonify(result), 200


@agent_bp.route("/decision/request", methods=["POST"])
def request_decision():
    data   = request.json or {}
    result = ai_service.request_decision(data)
    status = 503 if result.get("error") else 200
    return jsonify(result), status


# ── Agent 06: EHR ─────────────────────────────────────────────────────────────

@agent_bp.route("/ehr/<patient_id>", methods=["GET"])
def get_ehr(patient_id: str):
    result = ai_service.get_full_ehr(patient_id)
    return jsonify(result), 200


@agent_bp.route("/ehr/<patient_id>/summary", methods=["GET"])
def get_ehr_summary(patient_id: str):
    result = ai_service.get_patient_summary(patient_id)
    return jsonify(result), 200


@agent_bp.route("/ehr/<patient_id>/context", methods=["GET"])
def get_ehr_context(patient_id: str):
    result = ai_service.get_patient_context(patient_id)
    return jsonify(result), 200


@agent_bp.route("/ehr/<patient_id>/note", methods=["POST"])
def add_note(patient_id: str):
    data   = request.json or {}
    result = ai_service.add_clinical_note(patient_id, data)
    status = 503 if result.get("error") else 201
    return jsonify(result), status


# ── Agent 07: Medications ─────────────────────────────────────────────────────

@agent_bp.route("/medications/<patient_id>", methods=["GET"])
def get_medications(patient_id: str):
    result = ai_service.get_medications(patient_id)
    return jsonify(result), 200


@agent_bp.route("/medications/<patient_id>/analysis", methods=["GET"])
def get_medication_analysis(patient_id: str):
    result = ai_service.get_medication_analysis(patient_id)
    return jsonify(result), 200


@agent_bp.route("/medications/prescribe", methods=["POST"])
def prescribe():
    data   = request.json or {}
    result = ai_service.prescribe(data)
    status = 503 if result.get("error") else 201
    return jsonify(result), status


@agent_bp.route("/medications/interactions", methods=["POST"])
def check_interactions():
    data      = request.json or {}
    drug_list = data.get("medications", [])
    result    = ai_service.check_interactions(drug_list)
    return jsonify(result), 200


# ── Agent 08: Assistant ───────────────────────────────────────────────────────

@agent_bp.route("/chat", methods=["POST"])
def chat():
    data       = request.json or {}
    patient_id = data.get("patient_id")
    message    = data.get("message") or data.get("content")
    session_id = data.get("session_id")

    if not message:
        return jsonify({"error": "message is required"}), 400

    result = ai_service.chat_with_assistant(patient_id, message, session_id)
    status = 503 if result.get("error") else 200
    return jsonify(result), status


@agent_bp.route("/chat/history/<patient_id>", methods=["GET"])
def agent_chat_history(patient_id: str):
    result = ai_service.get_chat_history(patient_id)
    return jsonify(result), 200


# ── Agent 09: Analytics ───────────────────────────────────────────────────────

@agent_bp.route("/analytics/population", methods=["GET"])
def population_analytics():
    result = ai_service.get_population_analytics()
    return jsonify(result), 200


@agent_bp.route("/analytics/doctor/<doctor_id>", methods=["GET"])
def doctor_analytics(doctor_id: str):
    result = ai_service.get_doctor_analytics(doctor_id)
    return jsonify(result), 200


@agent_bp.route("/analytics/report", methods=["POST"])
def generate_report():
    data   = request.json or {}
    result = ai_service.generate_analytics_report(data.get("filters"))
    return jsonify(result), 200


# ── Agent 10: Emergency ───────────────────────────────────────────────────────

@agent_bp.route("/emergency/alerts", methods=["GET"])
def emergency_alerts():
    severity = request.args.get("severity")
    result   = ai_service.get_active_alerts(severity)
    return jsonify(result), 200


@agent_bp.route("/emergency/trigger", methods=["POST"])
def trigger_emergency():
    data   = request.json or {}
    result = ai_service.trigger_emergency(data)
    status = 503 if result.get("error") else 201
    return jsonify(result), status


@agent_bp.route("/emergency/acknowledge/<alert_id>", methods=["POST"])
def acknowledge_emergency(alert_id: str):
    data      = request.json or {}
    physician = data.get("physician", "On-Call Physician")
    result    = ai_service.acknowledge_alert(alert_id, physician)
    return jsonify(result), 200


@agent_bp.route("/emergency/resolve/<alert_id>", methods=["POST"])
def resolve_emergency(alert_id: str):
    data    = request.json or {}
    outcome = data.get("outcome", "Stabilized")
    result  = ai_service.resolve_alert(alert_id, outcome)
    return jsonify(result), 200


# ── Agent 11: Security ────────────────────────────────────────────────────────

@agent_bp.route("/security/compliance", methods=["GET"])
def compliance_report():
    result = ai_service.get_compliance_report()
    return jsonify(result), 200


@agent_bp.route("/security/audit", methods=["GET"])
def audit_logs():
    start  = request.args.get("from")
    end    = request.args.get("to")
    result = ai_service.get_audit_logs(start, end)
    return jsonify(result), 200
