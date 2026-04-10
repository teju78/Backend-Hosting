from database import db
from datetime import datetime
import uuid

class GeneratedReport(db.Model):
    __tablename__ = 'generated_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False) # Clinical, Ops, Research, etc.
    size = db.Column(db.String(20), nullable=False)
    format = db.Column(db.String(10), nullable=False) # PDF, EXCEL
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    data = db.Column(db.JSON, nullable=True) # Any extra data stored

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "type": self.type,
            "size": self.size,
            "format": self.format,
            "status": self.status,
            "date": self.created_at.strftime('%Y-%m-%d'),
            "created_at": self.created_at.isoformat()
        }
