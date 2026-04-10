from database import db
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.Enum('consultation', 'procedure', 'emergency', 'waiting'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    equipment = db.Column(db.JSON)
