from flask import Blueprint, request, jsonify
from database import db
from models import TriageRecord, Staff
from services.ai_service import ai_service
import uuid
from datetime import datetime

triage_bp = Blueprint('triage', __name__)


def _to_list(raw):
    """Convert any conditions/medications input (str, list, None) to a clean list."""
    if not raw or raw in ('None', '', 'none'):
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if x and str(x).strip() not in ('', 'None')]
    return [s.strip() for s in str(raw).split(',') if s.strip()]


@triage_bp.route('/', methods=['POST'])
@triage_bp.route('/submit', methods=['POST'])
def submit_symptoms():
    """
    Main entry point for Patient Portal Symptom Checker.
    1. Calls Agent 01 synchronously for instant triage result.
    2. Saves the triage record to the database.
    3. Fires the full Orchestrator pipeline in a background thread.
    4. Returns the FULL flat Agent 01 response to the frontend.
    """
    data       = request.json or {}
    symptoms   = data.get('symptoms') or data.get('symptom_text')
    patient_id = data.get('patient_id')
    severity   = int(data.get('severity', 5))
    duration   = int(data.get('duration', 1))
    conditions  = _to_list(data.get('conditions', []))
    medications = _to_list(data.get('medications', []))

    if not symptoms:
        return jsonify({"error": "symptoms is required"}), 400

    try:
        # ── Step 1: Call Agent 01 ─────────────────────────────────────────────
        analysis = ai_service.analyze_symptoms(
            patient_id  = patient_id,
            symptoms    = symptoms,
            severity    = severity,
            duration    = duration,
            age         = int(data.get('age', 35)),
            sex         = data.get('sex', 'Unknown'),
            conditions  = conditions,
            medications = medications,
        )

        if analysis.get('error'):
            raise Exception(analysis.get('detail', 'Agent 01 unavailable'))

        # Unwrap envelope if present
        if 'data' in analysis and isinstance(analysis['data'], dict):
            analysis = analysis['data']

        # ── Step 2: Persist to DB ─────────────────────────────────────────────
        label   = analysis.get('urgency_label', 'Routine').capitalize()
        db_tier = label if label in ('Emergency', 'Urgent', 'Routine', 'Self-care') else 'Routine'

        try:
            triage_id = analysis.get('triage_id')
            if triage_id and TriageRecord.query.get(triage_id):
                print(f"ℹ️ Triage {triage_id} already in DB — skipping duplicate write")
            else:
                on_duty = Staff.query.filter_by(role='doctor', is_on_duty=True).first()
                doctor_name = f"Dr. {on_duty.first_name} {on_duty.last_name}" if on_duty else "Queue — Pending Review"

                reasoning_list = analysis.get('reasoning', [])
                reasoning_str  = "\n".join(reasoning_list) if isinstance(reasoning_list, list) else str(reasoning_list)

                record = TriageRecord(
                    id                 = triage_id or str(uuid.uuid4()),
                    patient_id         = patient_id,
                    session_id         = str(uuid.uuid4()),
                    symptom_text       = symptoms,
                    duration           = str(duration),
                    severity_score     = severity,
                    urgency_tier       = db_tier,
                    reasoning          = reasoning_str,
                    recommended_action = analysis.get('recommended_action', 'Monitor symptoms.'),
                    icd10_hints        = analysis.get('icd10_hints', []),
                    drug_alerts        = analysis.get('drug_alerts', []),
                    assigned_doctor    = doctor_name,
                    created_at         = datetime.utcnow(),
                )

                # Add real-time notification
                from models import Notification
                notif = Notification(
                    patient_id=patient_id,
                    channel='in_app',
                    event_type='Health',
                    subject='Triage Evaluation Ready',
                    body=f"Your symptoms have been analyzed. Urgency: {db_tier}. Check your portal for the full plan.",
                    status='delivered'
                )

                db.session.add(record)
                db.session.add(notif)
                db.session.commit()
                print(f"✅ Triage record & notification saved — patient={patient_id}")
        except Exception as db_err:
            db.session.rollback()
            print(f"⚠️ DB write failed (returning result anyway): {db_err}")

        # ── Step 3: Trigger Orchestrator in background ────────────────────────
        try:
            import threading
            orch_payload = {
                "patient_id"  : str(patient_id or ""),
                "symptoms"    : symptoms,
                "severity"    : severity,
                "duration"    : duration,
                "age"         : data.get('age', 35),
                "sex"         : data.get('sex', 'Unknown'),
                "conditions"  : conditions,
                "medications" : medications,
            }
            threading.Thread(
                target=ai_service.orchestrate,
                args=(orch_payload,),
                daemon=True,
            ).start()
            print(f"🚀 Orchestrator triggered in background for patient={patient_id}")
        except Exception as orch_err:
            print(f"⚠️ Orchestrator trigger failed: {orch_err}")

        # ── Step 4: Return FULL flat Agent 01 Response ────────────────────────
        # Symptoms.jsx v5 reads all these fields directly from the response body:
        return jsonify({
            "status"               : "success",
            "triage_id"            : analysis.get("triage_id"),
            "patient_id"           : patient_id,
            # Urgency
            "urgency_tier"         : analysis.get("urgency_tier", 3),
            "urgency_label"        : analysis.get("urgency_label", "Routine"),
            "target_response"      : analysis.get("target_response", "Unknown"),
            # Clinical narrative
            "triage_summary"       : analysis.get("triage_summary", ""),
            "recommended_action"   : analysis.get("recommended_action", "Monitor symptoms."),
            # Diagnostics
            "differential_diagnosis": analysis.get("differential_diagnosis", []),
            "icd10_hints"          : analysis.get("icd10_hints", []),
            "icd10_suggestions"    : analysis.get("icd10_suggestions", []),
            # Risk & safety
            "red_flags_detected"   : analysis.get("red_flags_detected", []),
            "drug_alerts"          : analysis.get("drug_alerts", []),
            "news2_estimate"       : analysis.get("news2_estimate", 0),
            "comorbidity_risk"     : analysis.get("comorbidity_risk", 0.0),
            # AI metadata
            "reasoning"            : analysis.get("reasoning", []),
            "confidence"           : analysis.get("confidence", 0.0),
            "requires_alert"       : analysis.get("requires_alert", False),
            "llm_used"             : analysis.get("llm_used", False),
            "processing_ms"        : analysis.get("processing_ms", 0),
            "timestamp"            : analysis.get("timestamp", datetime.utcnow().isoformat()),
        }), 200

    except Exception as exc:
        import traceback
        traceback.print_exc()
        print(f"[triage] ERROR: {exc}")
        return jsonify({
            "status"            : "error",
            "message"           : str(exc),
            "urgency_label"     : "Unknown",
            "urgency_tier"      : 5,
            "reasoning"         : ["Agent service is currently synchronising."],
            "recommended_action": "Please contact the clinic directly.",
            "triage_id"         : None,
            "requires_alert"    : False,
        }), 200


@triage_bp.route('/analyze', methods=['POST'])
def analyze_symptoms():
    """Lighter triage-only endpoint (no DB write, no orchestrator)."""
    data       = request.json or {}
    symptoms   = data.get('symptoms')
    patient_id = data.get('patient_id')
    severity   = int(data.get('severity', 5))

    if not symptoms:
        return jsonify({"error": "Symptoms text is required"}), 400

    try:
        analysis = ai_service.analyze_symptoms(
            patient_id  = patient_id,
            symptoms    = symptoms,
            severity    = severity,
            duration    = int(data.get('duration', 1)),
            age         = int(data.get('age', 35)),
            sex         = data.get('sex', 'Unknown'),
            conditions  = _to_list(data.get('conditions', [])),
            medications = _to_list(data.get('medications', [])),
        )

        if analysis.get('error'):
            raise Exception(analysis.get('detail', 'Agent unavailable'))

        if 'data' in analysis and isinstance(analysis['data'], dict):
            analysis = analysis['data']

        label = analysis.get('urgency_label', 'Routine').capitalize()
        db_tier = label if label in ('Emergency', 'Urgent', 'Routine', 'Self-care') else 'Routine'

        on_duty = Staff.query.filter_by(role='doctor', is_on_duty=True).first()
        doctor_name = f"Dr. {on_duty.first_name} {on_duty.last_name}" if on_duty else "Queue - Pending Review"

        reasoning_list = analysis.get('reasoning', [])
        reasoning_str  = "\n".join(reasoning_list) if isinstance(reasoning_list, list) else str(reasoning_list)

        record = TriageRecord(
            id                 = analysis.get('triage_id', str(uuid.uuid4())),
            patient_id         = patient_id,
            session_id         = str(uuid.uuid4()),
            symptom_text       = symptoms,
            severity_score     = severity,
            urgency_tier       = db_tier,
            reasoning          = reasoning_str,
            recommended_action = analysis.get('recommended_action', "Follow up if symptoms persist."),
            icd10_hints        = analysis.get('icd10_hints', []),
            drug_alerts        = analysis.get('drug_alerts', []),
            assigned_doctor    = doctor_name,
            created_at         = datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            "id"      : record.id,
            "urgency" : analysis.get('urgency_label', 'Routine'),
            "tier"    : analysis.get('urgency_tier', 3),
            "reasoning": analysis.get('triage_summary', 'Evaluation complete.'),
            "status"  : "success"
        }), 201

    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 500


@triage_bp.route('/history/<patient_id>', methods=['GET'])
def get_triage_history(patient_id):
    records = TriageRecord.query.filter_by(patient_id=patient_id).order_by(
        TriageRecord.created_at.desc()
    ).limit(20).all()
    return jsonify([{
        "id"              : r.id,
        "symptoms"        : r.symptom_text,
        "urgency"         : r.urgency_tier,
        "recommended_action": r.recommended_action,
        "icd10_hints"     : r.icd10_hints or [],
        "drug_alerts"     : r.drug_alerts or [],
        "assigned_doctor" : r.assigned_doctor,
        "date"            : r.created_at.isoformat() if r.created_at else None,
    } for r in records]), 200
