from flask import Blueprint, request, jsonify, current_app
from database import db
from models import User
import bcrypt
import jwt
import datetime
import os
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'patient')
    first_name = data.get('first_name', 'Unnamed')
    last_name = data.get('last_name', 'User')
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 400
        
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_id = str(uuid.uuid4())
    
    patient_id = None
    staff_id = None
    
    from models import Patient, Staff
    
    if role == 'patient':
        from cryptography.fernet import Fernet
        # Use the same key as the EHR system
        key = b'ONmBNnKyRqnbbm85R8K60XlSjpbSn7KYNhw27dQgE9M='
        cipher = Fernet(key)
        
        patient_id = str(uuid.uuid4())
        
        # Pull clinical demographics from request
        dob         = data.get('dob', '2000-01-01')
        gender      = data.get('gender', 'unknown')
        blood_group = data.get('blood_group', 'O+')

        new_patient = Patient(
            id=patient_id,
            mrn=f"MRN-{str(uuid.uuid4())[:8].upper()}",
            first_name_enc = cipher.encrypt(first_name.encode('utf-8')),
            last_name_enc  = cipher.encrypt(last_name.encode('utf-8')),
            dob_enc        = cipher.encrypt(dob.encode('utf-8')),
            gender         = gender,
            blood_group    = blood_group
        )
        db.session.add(new_patient)
    elif role in ['doctor', 'nurse', 'dentist']:
        staff_id = str(uuid.uuid4())
        new_staff = Staff(
            id=staff_id,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_on_duty=True
        )
        db.session.add(new_staff)

    new_user = User(
        id=user_id,
        email=email,
        password_hash=hashed_pw,
        role=role,
        patient_id=patient_id,
        staff_id=staff_id
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    use_keycloak = data.get('use_keycloak', False)
    
    # Simulating Keycloak Token Exchange
    if use_keycloak:
        # In a real app, you'd call Keycloak token endpoint here
        # POST {KEYCLOAK_URL}/auth/realms/{REALM}/protocol/openid-connect/token
        # grant_type=password, client_id, client_secret, username, password
        
        KEYCLOAK_MOCK_SUCCESS = True # Toggle for demo
        if KEYCLOAK_MOCK_SUCCESS:
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"error": "Identity not found in synchronized cluster"}), 401
                
            token = jwt.encode({
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'iss': 'keycloak.mediagents.ai',
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm='HS256')
            
            user_data = {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "patient_id": user.patient_id,
                "staff_id": user.staff_id
            }

            if user.patient_id:
                from models import Patient
                p = Patient.query.get(user.patient_id)
                if p:
                    user_data["name"] = f"{p.first_name} {p.last_name}"
            elif user.staff_id:
                from models import Staff
                s = Staff.query.get(user.staff_id)
                if s:
                    user_data["name"] = f"{s.first_name} {s.last_name}"

            return jsonify({
                "token": token,
                "provider": "keycloak",
                "user": user_data
            }), 200
    
    # Fallback to Local Auth
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({"error": "Invalid credentials"}), 401
        
    token = jwt.encode({
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    # Prepare user data for response
    user_data = {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "patient_id": user.patient_id,
        "staff_id": user.staff_id
    }

    # Try to add name
    if user.patient_id:
        from models import Patient
        p = Patient.query.get(user.patient_id)
        if p:
            user_data["name"] = f"{p.first_name} {p.last_name}"
    elif user.staff_id:
        from models import Staff
        s = Staff.query.get(user.staff_id)
        if s:
            user_data["name"] = f"{s.first_name} {s.last_name}"
    
    return jsonify({
        "token": token,
        "user": user_data
    }), 200
@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.split(' ')[1]
    try:
        decoded = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded.get('user_id')
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not bcrypt.checkpw(current_password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return jsonify({"error": "Invalid current password"}), 400
        
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password_hash = hashed_pw
        db.session.commit()
        
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 401
