from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.String(100))
    note_type = db.Column(db.String(50))
    subjective = db.Column(db.Text)
    objective = db.Column(db.Text)
    assessment = db.Column(db.Text)
    plan = db.Column(db.Text)
    free_text = db.Column(db.Text)
    is_signed = db.Column(db.Boolean, default=False)
    signed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
