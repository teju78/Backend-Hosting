from database import db
from datetime import datetime

class AlertThreshold(db.Model):
    __tablename__ = 'alert_thresholds'
    
    id = db.Column(db.String(50), primary_key=True)  # e.g., 'hr', 'spo2', 'resp', 'temp'
    label = db.Column(db.String(100), nullable=False)
    unit = db.Column(db.String(20))
    e_min = db.Column(db.Float)
    e_max = db.Column(db.Float)
    u_min = db.Column(db.Float)
    u_max = db.Column(db.Float)
    is_enabled = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "unit": self.unit,
            "eMin": self.e_min,
            "eMax": self.e_max,
            "uMin": self.u_min,
            "uMax": self.u_max,
            "enabled": self.is_enabled
        }

class EscalationRule(db.Model):
    __tablename__ = 'escalation_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    rule_text = db.Column(db.String(255), nullable=False)
    action_text = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='Active') # 'Active', 'Disabled'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "rule": self.rule_text,
            "action": self.action_text,
            "status": self.status
        }
