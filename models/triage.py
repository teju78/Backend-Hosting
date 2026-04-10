from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class TriageRecord(db.Model):
    __tablename__ = 'triage_records'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'))
    session_id = db.Column(db.String(36), nullable=False)
    symptom_text = db.Column(db.Text)
    duration = db.Column(db.String(100))
    severity_score = db.Column(db.Integer)
    urgency_tier = db.Column(db.Enum('Emergency', 'Urgent', 'Routine', 'Self-care'), nullable=False)
    reasoning = db.Column(db.Text)
    recommended_action = db.Column(db.Text)
    icd10_hints = db.Column(db.JSON)
    drug_alerts = db.Column(db.JSON)
    risk_analysis = db.Column(db.JSON)       # Agent 04 output
    medication_analysis = db.Column(db.JSON) # Agent 07 output
    decision_support = db.Column(db.JSON)    # Agent 05 output
    assigned_doctor = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
