from database import db
from datetime import datetime

class MedicationDose(db.Model):
    __tablename__ = 'medication_doses'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'))
    drug_code = db.Column(db.String(50))
    scheduled_time = db.Column(db.DateTime)
    dose_taken = db.Column(db.Boolean, default=False)
    taken_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
