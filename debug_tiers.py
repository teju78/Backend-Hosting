from database import db
from models import TriageRecord
from app import create_app

app, socketio = create_app()
with app.app_context():
    print("CHECKING URGENCY TIERS...")
    tiers = db.session.query(TriageRecord.urgency_tier, TriageRecord.symptoms).all()
    for t in tiers:
        print(f"Tier: {t[0]}, Symptoms: {t[1][:50] if t[1] else 'None'}")
