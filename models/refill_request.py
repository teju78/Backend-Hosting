from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class RefillRequest(db.Model):
    __tablename__ = 'refill_requests'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    drug_name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
