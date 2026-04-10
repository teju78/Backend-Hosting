from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class PatientVitals(db.Model):
    __tablename__ = 'patient_vitals'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    hr = db.Column(db.Numeric(5, 2))      # Heart Rate (bpm)
    bp_sys = db.Column(db.Numeric(5, 2))  # Systolic Blood Pressure
    bp_dia = db.Column(db.Numeric(5, 2))  # Diastolic Blood Pressure
    spo2 = db.Column(db.Numeric(5, 2))    # Oxygen Saturation (%)
    temp_c = db.Column(db.Numeric(4, 2))  # Temperature (Celsius)
    rr = db.Column(db.Numeric(4, 2))      # Respiratory Rate
    glucose = db.Column(db.Numeric(5, 2)) # Blood Glucose (mg/dL)
    news2_score = db.Column(db.Integer)   # National Early Warning Score 2
    measured_at = db.Column(db.DateTime, default=datetime.utcnow)

    recorded_by = db.Column(db.String(36), db.ForeignKey('staff.id')) # Optional
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
