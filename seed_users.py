from app import create_app
from database import db
from models import User
import bcrypt
import uuid

def seed_users():
    app, socketio = create_app()
    with app.app_context():
        # Define users to create
        users = [
            {"email": "patient@clinic.ai", "password": "password123", "role": "patient"},
            {"email": "doctor@clinic.ai", "password": "password123", "role": "doctor"},
            {"email": "admin@clinic.ai", "password": "password123", "role": "admin"},
        ]

        for u in users:
            if not User.query.filter_by(email=u['email']).first():
                hashed_pw = bcrypt.hashpw(u['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                new_user = User(
                    id=str(uuid.uuid4()),
                    email=u['email'],
                    password_hash=hashed_pw,
                    role=u['role']
                )
                db.session.add(new_user)
                print(f"Created user: {u['email']} ({u['role']})")
            else:
                print(f"User already exists: {u['email']}")
        
        db.session.commit()
        print("Seeding complete.")

if __name__ == "__main__":
    seed_users()
