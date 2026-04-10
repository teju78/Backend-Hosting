from database import db
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    mrn = db.Column(db.String(20), unique=True, nullable=False)
    first_name_enc = db.Column(db.LargeBinary, nullable=False)
    last_name_enc = db.Column(db.LargeBinary, nullable=False)
    dob_enc = db.Column(db.LargeBinary, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'other', 'unknown'), default='unknown')
    language_pref = db.Column(db.String(10), default='en')
    phone_enc = db.Column(db.LargeBinary)
    email_enc = db.Column(db.LargeBinary)
    blood_group = db.Column(db.String(5))
    height = db.Column(db.String(50))
    weight = db.Column(db.String(50))
    
    
    # Notification Preferences
    pref_health_updates = db.Column(db.Boolean, default=True)
    pref_appointments = db.Column(db.Boolean, default=True)
    pref_medication = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def first_name(self):
        return self._decrypt(self.first_name_enc)
    
    @property
    def last_name(self):
        return self._decrypt(self.last_name_enc)
    
    @property
    def dob(self):
        return self._decrypt(self.dob_enc)
    
    @property
    def phone(self):
        return self._decrypt(self.phone_enc)
    
    @property
    def email(self):
        return self._decrypt(self.email_enc)

    def _decrypt(self, v):
        if not v or v == 'None': return None
        try:
            from cryptography.fernet import Fernet
            key = b'ONmBNnKyRqnbbm85R8K60XlSjpbSn7KYNhw27dQgE9M='
            cipher_suite = Fernet(key)
            
            # Normalize to bytes for check
            buf = bytes(v) if isinstance(v, (memoryview, bytearray)) else v
            
            # 1. Standard Fernet Decryption
            if isinstance(buf, bytes) and buf.startswith(b'gAAAA'):
                try:
                    return cipher_suite.decrypt(buf).decode('utf-8')
                except:
                    pass
            
            # 2. Repair contaminated string data
            s = buf.decode('utf-8', 'ignore') if isinstance(buf, bytes) else str(v)
            s = s.strip()
            
            import re
            for _ in range(5):
                s = re.sub(r"^[bB]['\"](.*)[\"']$", r"\1", s).strip()
                s = s.strip("'\" ")
            return s
        except Exception:
            return str(v).strip()
