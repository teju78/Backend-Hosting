from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=False)
    channel = db.Column(db.Enum('push', 'sms', 'email', 'in_app'), nullable=False)
    event_type = db.Column(db.String(50))
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    status = db.Column(db.Enum('queued', 'sent', 'delivered', 'failed'), default='queued')
    external_id = db.Column(db.String(100))
    sent_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
