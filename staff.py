from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('patient', 'doctor', 'nurse', 'admin', 'radiologist', 'dentist'), nullable=False)
    speciality = db.Column(db.String(100))
    license_number = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    is_on_duty = db.Column(db.Boolean, default=False)
    is_busy = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
