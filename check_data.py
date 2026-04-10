import sys
import os

# Add the current directory to path
sys.path.append(os.getcwd())

def decrypt_val(v):
    if not v: return None
    try:
        from cryptography.fernet import Fernet
        key = b'ONmBNnKyRqnbbm85R8K60XlSjpbSn7KYNhw27dQgE9M='
        cipher_suite = Fernet(key)
        buf = bytes(v) if isinstance(v, (memoryview, bytearray)) else v
        if isinstance(buf, bytes) and buf.startswith(b'gAAAA'):
            return cipher_suite.decrypt(buf).decode('utf-8')
        return buf.decode('utf-8', 'ignore') if isinstance(buf, bytes) else str(v)
    except:
        return str(v)

try:
    from app import create_app
    from database import db
    from models.patient import Patient
    
    app, _ = create_app()
    with app.app_context():
        patients = db.session.query(Patient).all()
        print(f"PATIENT_COUNT:{len(patients)}")
        for p in patients:
            fname = decrypt_val(p.first_name_enc)
            lname = decrypt_val(p.last_name_enc)
            print(f"ID:{p.id} | MRN:{p.mrn} | NAME:{fname} {lname}")
except Exception as e:
    import traceback
    print(f"ERROR:{str(e)}")
    traceback.print_exc()
