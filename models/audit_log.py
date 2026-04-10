from database import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(36))
    user_role = db.Column(db.String(20))
    action = db.Column(db.String(50), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.String(36))
    patient_id = db.Column(db.String(36))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    is_anomalous = db.Column(db.Boolean, default=False)
    details = db.Column(db.JSON)
