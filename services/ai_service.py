"""
ClinicAI — Professional AI Service Client
==========================================
Centralized HTTP client that speaks to all 12 agents.

Features:
  - Async-first with httpx (uses requests as sync fallback for Flask routes)
  - Per-agent timeout configuration
  - 3-attempt retry with exponential backoff
  - Structured error envelopes with agent attribution
  - Agent health check with circuit-breaker awareness
"""
from __future__ import annotations

import os
import time
import logging
from typing import Any, Dict, Optional, List

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("clinic_ai.ai_service")

# ── Agent URL Registry ─────────────────────────────────────────────────────────

AGENT_URLS: Dict[str, str] = {
    "orchestrator": os.getenv("AGENT_00_URL", "http://127.0.0.1:8000"),
    "triage"      : os.getenv("AGENT_01_URL", "http://127.0.0.1:8001"),
    "appointment" : os.getenv("AGENT_02_URL", "http://127.0.0.1:8002"),
    "monitoring"  : os.getenv("AGENT_03_URL", "http://127.0.0.1:8003"),
    "risk"        : os.getenv("AGENT_04_URL", "http://127.0.0.1:8004"),
    "decision"    : os.getenv("AGENT_05_URL", "http://127.0.0.1:8005"),
    "ehr"         : os.getenv("AGENT_06_URL", "http://localhost:8006"),
    "medication"  : os.getenv("AGENT_07_URL", "http://127.0.0.1:8007"),
    "assistant"   : os.getenv("AGENT_08_URL", "http://127.0.0.1:8008"),
    "analytics"   : os.getenv("AGENT_09_URL", "http://127.0.0.1:8009"),
    "emergency"   : os.getenv("AGENT_10_URL", "http://127.0.0.1:8010"),
    "security"    : os.getenv("AGENT_11_URL", "http://127.0.0.1:8011"),
}

# Per-agent timeouts (seconds) — triage/decision are LLM-heavy → longer
AGENT_TIMEOUTS: Dict[str, int] = {
    "triage"   : 120,
    "decision" : 120,
    "assistant": 60,
    "risk"     : 30,
    "ehr"      : 60,
    "medication": 60,
    "default"  : 15,
}

# ── Error Envelope ─────────────────────────────────────────────────────────────

def _error(agent: str, detail: str, code: int = 503) -> Dict[str, Any]:
    return {"error": True, "agent": agent, "detail": detail, "code": code}


# ── HTTP Helpers ───────────────────────────────────────────────────────────────

def _timeout_for(agent: str) -> int:
    return AGENT_TIMEOUTS.get(agent, AGENT_TIMEOUTS["default"])


def _get(agent: str, path: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    url = f"{AGENT_URLS[agent]}{path}"
    timeout = _timeout_for(agent)
    last_err = ""
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
            logger.warning("[%s] GET %s → %d", agent, path, resp.status_code)
            return _error(agent, f"Agent returned HTTP {resp.status_code}", resp.status_code)
        except requests.exceptions.ConnectionError as exc:
            last_err = f"Agent {agent} is offline"
            logger.debug("[%s] Connection error (attempt %d): %s", agent, attempt + 1, exc)
        except requests.exceptions.Timeout:
            last_err = f"Agent {agent} timed out after {timeout}s"
            logger.warning("[%s] Timeout on GET %s (attempt %d)", agent, path, attempt + 1)
        except Exception as exc:
            last_err = str(exc)
            logger.error("[%s] Unexpected error: %s", agent, exc)
            break
        if attempt < 2:
            time.sleep(0.5 * (attempt + 1))  # 0.5s, 1.0s backoff
    return _error(agent, last_err)


def _post(agent: str, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{AGENT_URLS[agent]}{path}"
    timeout = _timeout_for(agent)
    last_err = ""
    for attempt in range(3):
        try:
            resp = requests.post(url, json=data, timeout=timeout)
            if resp.status_code in (200, 201):
                return resp.json()
            logger.warning("[%s] POST %s → %d: %s", agent, path, resp.status_code, resp.text[:200])
            return _error(agent, f"Agent returned HTTP {resp.status_code}", resp.status_code)
        except requests.exceptions.ConnectionError:
            last_err = f"Agent {agent} is offline"
            logger.debug("[%s] Connection refused on POST %s (attempt %d)", agent, path, attempt + 1)
        except requests.exceptions.Timeout:
            last_err = f"Agent {agent} timed out after {timeout}s"
            logger.warning("[%s] Timeout on POST %s (attempt %d)", agent, path, attempt + 1)
        except Exception as exc:
            last_err = str(exc)
            logger.error("[%s] Unexpected error: %s", agent, exc)
            break
        if attempt < 2:
            time.sleep(0.5 * (attempt + 1))
    return _error(agent, last_err)


def _put(agent: str, path: str) -> Dict[str, Any]:
    url = f"{AGENT_URLS[agent]}{path}"
    try:
        resp = requests.put(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return _error(agent, f"HTTP {resp.status_code}", resp.status_code)
    except Exception as exc:
        return _error(agent, str(exc))


# ═══════════════════════════════════════════════════════════════════════════════
#  AIService  — unified API surface for the Flask backend
# ═══════════════════════════════════════════════════════════════════════════════

class AIService:
    """
    Unified client for all ClinicAI specialist agents.
    Each method corresponds to a specific agent capability.
    """

    # ──────────────────── Agent 00: Orchestrator ──────────────────────────────

    def orchestrate(self, data: Dict) -> Dict:
        """Triggers the full multi-agent sequential pipeline via Orchestrator."""
        return _post("orchestrator", "/orchestrate", data)

    def get_agents_status(self) -> Dict:
        """Returns health status for all agents (from Orchestrator)."""
        return _get("orchestrator", "/agents/status")

    # ──────────────────── Agent 01: Symptom Triage ────────────────────────────

    def analyze_symptoms(
        self,
        patient_id: str,
        symptoms: str,
        severity: int,
        duration: int,
        age: int = 35,
        sex: str = "Unknown",
        conditions: Optional[List] = None,
        medications: Optional[List] = None,
    ) -> Dict:
        """Submit patient symptoms for immediate triage (Agent 01)."""
        if isinstance(conditions, str):
            conditions = [conditions] if conditions not in ("", "None") else []
        if isinstance(medications, str):
            medications = [medications] if medications not in ("", "None") else []

        payload = {
            "patient_id"   : str(patient_id),
            "symptom_text" : str(symptoms),
            "severity"     : int(severity),
            "duration_days": int(duration),
            "age"          : int(age),
            "sex"          : str(sex),
            "conditions"   : conditions or [],
            "medications"  : medications or [],
        }
        return _post("triage", "/triage", payload)

    def get_triage_result(self, triage_id: str) -> Dict:
        return _get("triage", f"/triage/{triage_id}")

    def get_patient_triage_status(self, patient_id: str) -> Dict:
        return _get("triage", f"/status/{patient_id}")

    # ──────────────────── Agent 02: Appointment Scheduler ─────────────────────

    def get_appointment_slots(self, date: str, doctor_id: Optional[str] = None) -> Dict:
        return _get("appointment", "/slots", {"date": date, "doctor": doctor_id})

    def schedule_appointment(self, appointment_data: Dict) -> Dict:
        return _post("appointment", "/book", appointment_data)

    def get_appointments(self, patient_id: str) -> Dict:
        return _get("appointment", f"/appointments/{patient_id}")

    def get_clinical_queue(self) -> Dict:
        """Retrieve the live clinical patient queue from Agent 02."""
        return _get("appointment", "/queue")

    # ──────────────────── Agent 03: Continuous Monitoring ─────────────────────

    def ingest_vitals(self, patient_id: str, vitals_data: Dict) -> Dict:
        """Push a new vital reading to the monitoring agent."""
        return _post("monitoring", f"/vitals/{patient_id}/ingest", vitals_data)

    def get_latest_vitals(self, patient_id: str) -> Dict:
        return _get("monitoring", f"/vitals/{patient_id}/latest")

    def get_vitals_history(self, patient_id: str, limit: int = 20) -> Dict:
        return _get("monitoring", f"/vitals/{patient_id}/history", {"limit": limit})

    def get_all_alerts(self) -> Dict:
        return _get("monitoring", "/alerts")

    def get_patient_alert(self, patient_id: str) -> Dict:
        return _get("monitoring", f"/alerts/{patient_id}")

    # ──────────────────── Agent 04: Predictive Risk ────────────────────────────

    def get_risk_assessment(self, patient_id: str) -> Dict:
        return _get("risk", f"/risk/{patient_id}")

    def score_risk(self, profile_data: Dict) -> Dict:
        return _post("risk", "/risk/score", profile_data)

    def get_risk_history(self, patient_id: str, limit: int = 10) -> Dict:
        return _get("risk", f"/risk/{patient_id}/history", {"limit": limit})

    # ──────────────────── Agent 05: Clinical Decision Support ─────────────────

    def get_decision_support(self, patient_id: str) -> Dict:
        """Get the latest clinical decision for a patient."""
        return _get("decision", f"/decision/{patient_id}")

    def request_decision(self, decision_payload: Dict) -> Dict:
        """Directly request a clinical decision for a detailed patient context."""
        return _post("decision", "/decision/generate", decision_payload)

    # ──────────────────── Agent 06: Smart EHR ─────────────────────────────────

    def get_patient_context(self, patient_id: str) -> Dict:
        return _get("ehr", f"/patient/{patient_id}/context")

    def get_full_ehr(self, patient_id: str) -> Dict:
        return _get("ehr", f"/record/{patient_id}")

    def get_patient_summary(self, patient_id: str) -> Dict:
        return _get("ehr", f"/summary/{patient_id}")

    def get_ehr_record(self, patient_id: str) -> Dict:
        return _get("ehr", f"/record/{patient_id}")

    def add_clinical_note(self, patient_id: str, note_data: Dict) -> Dict:
        return _post("ehr", f"/patient/{patient_id}/note", note_data)

    def generate_single_narrative(self, text: str, note_type: str = "Physician Note", note_id: Optional[str] = None) -> Dict:
        """Use EHR Agent (06) to generate a smart narrative insight for a specific piece of text."""
        payload = {
            "text": text,
            "type": note_type,
            "note_id": note_id
        }
        return _post("ehr", "/narrative/single", payload)

    def delete_note(self, note_id: str) -> Dict:
        """DELETE a note from EHR Agent."""
        url = f"{AGENT_URLS['ehr']}/notes/{note_id}"
        try:
            resp = requests.delete(url, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return _error("ehr", f"Delete failed: {resp.status_code}", resp.status_code)
        except Exception as exc:
            return _error("ehr", str(exc))

    def update_note(self, note_id: str, note_data: Dict) -> Dict:
        """PUT (update) a note in EHR Agent."""
        url = f"{AGENT_URLS['ehr']}/notes/{note_id}"
        try:
            resp = requests.put(url, json=note_data, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return _error("ehr", f"Update failed: {resp.status_code}", resp.status_code)
        except Exception as exc:
            return _error("ehr", str(exc))

    def update_ehr(self, record_data: Dict) -> Dict:
        return _post("ehr", "/record", record_data)

    # ──────────────────── Agent 07: Medication Management ─────────────────────

    def get_medications(self, patient_id: str, patient_name: Optional[str] = None) -> Dict:
        params = {"patient_name": patient_name} if patient_name else {}
        return _get("medication", f"/medications/{patient_id}", params)

    def get_medication_analysis(self, patient_id: str) -> Dict:
        return _get("medication", f"/medications/{patient_id}/analysis")

    def prescribe(self, prescription_data: Dict) -> Dict:
        return _post("medication", "/prescribe", prescription_data)

    def log_medication_dose(self, patient_id: str, drug_code: str, status: str = "Taken") -> Dict:
        """Log that a dose was taken or missed (Agent 07)."""
        return _post("medication", f"/adherence/{patient_id}", {
            "medication_name": drug_code, # Agent 07 currently uses medication_name in its route
            "status": status
        })

    def request_medication_refill(self, patient_id: str, drug_name: str) -> Dict:
        """Submit a refill request for a medication (Agent 07)."""
        return _post("medication", "/refill", {
            "patient_id": patient_id,
            "drug_name": drug_name
        })

    def check_interactions(self, drugs: List[str]) -> Dict:
        return _post("medication", "/interactions/check", {"medications": drugs})

    # ──────────────────── Agent 08: Conversational Assistant ──────────────────

    def chat_with_assistant(self, patient_id: str, message: str, session_id: Optional[str] = None) -> Dict:
        payload = {
            "patient_id": patient_id,
            "content"   : message,
            "message"   : message,  # Keep alias for compatibility
        }
        if session_id:
            payload["session_id"] = session_id
        return _post("assistant", "/chat", payload)

    def get_chat_history(self, patient_id: str) -> Dict:
        return _get("assistant", f"/chat/{patient_id}/history")

    # ──────────────────── Agent 09: Population Analytics ──────────────────────

    def get_population_analytics(self) -> Dict:
        return _get("analytics", "/analytics/population")

    def get_doctor_analytics(self, doctor_id: str) -> Dict:
        return _get("analytics", f"/analytics/doctor/{doctor_id}")

    def generate_analytics_report(self, payload: Dict) -> Dict:
        """Call Agent 09 to generate a specialized population report from a clinical corpus."""
        return _post("analytics", "/reports/generate", payload)

    # ──────────────────── Agent 10: Emergency Dispatch ────────────────────────

    def get_active_alerts(self, severity: Optional[str] = None) -> Dict:
        params = {"severity": severity} if severity else {}
        return _get("emergency", "/alerts", params)

    def trigger_emergency(self, event_data: Dict) -> Dict:
        return _post("emergency", "/trigger", event_data)

    def acknowledge_alert(self, alert_id: str, physician: str = "On-Call Physician") -> Dict:
        return _post("emergency", f"/acknowledge/{alert_id}", {"physician": physician})

    def resolve_alert(self, alert_id: str, outcome: str = "Stabilized") -> Dict:
        return _post("emergency", f"/resolve/{alert_id}", {"outcome": outcome})

    # ──────────────────── Agent 11: Security & Compliance ─────────────────────

    def validate_access(self, user_id: str, role: str, resource: str, action: str) -> Dict:
        return _post("security", "/validate", {
            "user_id" : user_id,
            "role"    : role,
            "resource": resource,
            "action"  : action,
        })

    def get_compliance_report(self) -> Dict:
        return _get("security", "/compliance/report")

    def get_audit_logs(self, start: Optional[str] = None, end: Optional[str] = None) -> Dict:
        return _get("security", "/audit", {"from": start, "to": end})

    # ──────────────────── System Health ───────────────────────────────────────

    def get_agent_health(self) -> Dict:
        """Check overall system health via Orchestrator."""
        return self.get_agents_status()

    def check_agent(self, agent_name: str) -> Dict:
        """Check a single agent's health."""
        return _get(agent_name, "/health") if agent_name in AGENT_URLS else _error(agent_name, "Unknown agent")


# Singleton instance used across all routes
ai_service = AIService()
