from database import db
from datetime import datetime

class AlertAcknowledgment(db.Model):
    __tablename__ = 'alert_acknowledgments'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    acknowledged_by = db.Column(db.String(100))
    acknowledged_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AlertAcknowledgment {self.alert_key}>'
