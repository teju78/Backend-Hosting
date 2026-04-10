from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.String(36), db.ForeignKey('staff.id'))
    drug_name = db.Column(db.String(200), nullable=False)
    drug_code = db.Column(db.String(50))
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    route = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.Enum('active', 'completed', 'discontinued', 'on_hold'), default='active')
    adherence_score = db.Column(db.Numeric(5, 2), default=100.00)
    refill_due_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
