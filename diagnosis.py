from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), nullable=False)
    doctor_id = db.Column(db.String(36), nullable=True)
    icd10_code = db.Column(db.String(10), nullable=True)
    icd10_description = db.Column(db.String(255), nullable=True)
    status = db.Column(db.Enum('active','resolved','chronic','ruled_out'), default='active')
    onset_date = db.Column(db.Date, nullable=True)
    resolved_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'icd10_code': self.icd10_code,
            'icd10_description': self.icd10_description,
            'status': self.status,
            'onset_date': self.onset_date.isoformat() if self.onset_date else None,
            'resolved_date': self.resolved_date.isoformat() if self.resolved_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
