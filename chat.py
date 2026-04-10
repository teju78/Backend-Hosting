from database import db
from datetime import datetime
import uuid

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.String(36), index=True, nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    intent = db.Column(db.String(50))
    metadata_json = db.Column(db.JSON) # Any extra data like escalation_required

    def to_dict(self):
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "intent": self.intent
        }
