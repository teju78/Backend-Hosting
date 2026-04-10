"""
ClinicAI — Monitoring & Vitals Routes  /api/monitoring/*
=========================================================
Real-time vitals ingestion, live alerts, and vital history.
"""
from flask import Blueprint, request, jsonify
from services.ai_service import ai_service
from database import db

monitoring_bp = Blueprint("monitoring", __name__)


@monitoring_bp.route("/ingest/<patient_id>", methods=["POST"])
def ingest_vitals(patient_id: str):
    """
    POST /api/monitoring/ingest/{patient_id}
    Body: { heart_rate, sys_bp, dia_bp, temp, spo2, ... }
    Pushes a new vital reading to Agent 03 for analysis.
    """
    data = request.json or {}
    if not data:
        return jsonify({"error": "Vitals data is required"}), 400

    result = ai_service.ingest_vitals(patient_id, data)
    if result.get("error"):
        return jsonify({
            "error"  : True,
            "detail" : result.get("detail", "Monitoring agent unavailable"),
            "vitals" : data,
            "status" : "queued_for_retry"
        }), 200  # Return 200 so UI still receives the vitals data

    return jsonify(result), 200


@monitoring_bp.route("/vitals/<patient_id>", methods=["GET"])
def get_latest_vitals(patient_id: str):
    """GET /api/monitoring/vitals/{patient_id} — Latest vitals reading."""
    result = ai_service.get_latest_vitals(patient_id)
    if result.get("error"):
        return jsonify({"patient_id": patient_id, "vitals": None, "status": "unavailable"}), 200
    return jsonify(result), 200


@monitoring_bp.route("/vitals/<patient_id>/history", methods=["GET"])
def get_vitals_history(patient_id: str):
    """GET /api/monitoring/vitals/{patient_id}/history — Vitals trend data."""
    limit  = int(request.args.get("limit", 20))
    result = ai_service.get_vitals_history(patient_id, limit)
    return jsonify(result), 200


@monitoring_bp.route("/alerts", methods=["GET"])
def get_all_monitoring_alerts():
    """GET /api/monitoring/alerts — All active high-urgency patient alerts."""
    result = ai_service.get_all_alerts()
    return jsonify(result), 200


@monitoring_bp.route("/alerts/<patient_id>", methods=["GET"])
def get_patient_alerts(patient_id: str):
    """GET /api/monitoring/alerts/{patient_id} — Alerts for specific patient."""
    result = ai_service.get_patient_alert(patient_id)
    return jsonify(result), 200


@monitoring_bp.route("/status", methods=["GET"])
def monitoring_status():
    """GET /api/monitoring/status — Monitoring agent health."""
    result = ai_service.check_agent("monitoring")
    return jsonify(result), 200
