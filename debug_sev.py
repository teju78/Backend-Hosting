from database import db
from models import TriageRecord
from sqlalchemy import func
from app import create_app

app, socketio = create_app()
with app.app_context():
    avg = db.session.query(func.avg(TriageRecord.severity_score)).scalar()
    print(f"AVG SEV: {avg}")
