from app import create_app
from database import db
from models import AlertAcknowledgment
import logging

app, _ = create_app()
with app.app_context():
    print("Checking AlertAcknowledgment entries...")
    try:
        count = AlertAcknowledgment.query.count()
        print(f"Total entries: {count}")
        last = AlertAcknowledgment.query.order_by(AlertAcknowledgment.id.desc()).first()
        if last:
            print(f"Last entry: {last.alert_key} by {last.acknowledged_by}")
    except Exception as e:
        print(f"Error: {e}")
