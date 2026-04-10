from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class LabOrder(db.Model):
    __tablename__ = 'lab_orders'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'))
    doctor_id = db.Column(db.String(36), db.ForeignKey('staff.id'))
    test_name = db.Column(db.String(200), nullable=False)
    loinc_code = db.Column(db.String(20))
    status = db.Column(db.Enum('ordered', 'collected', 'processing', 'resulted', 'cancelled'), default='ordered')
    priority = db.Column(db.Enum('routine', 'urgent', 'stat'), default='routine')
    ordered_at = db.Column(db.DateTime, default=datetime.utcnow)
    resulted_at = db.Column(db.DateTime)
    result_value = db.Column(db.Numeric(10, 4))
    result_unit = db.Column(db.String(30))
    result_text = db.Column(db.Text)
    reference_range = db.Column(db.String(50))
    is_abnormal = db.Column(db.Boolean, default=False)
    result_narrative = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
