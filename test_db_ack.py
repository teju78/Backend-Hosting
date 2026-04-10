import sys
import os
sys.path.append(os.getcwd())

from app import create_app
from database import db
from models import AlertAcknowledgment
from datetime import datetime

app, _ = create_app()
with app.app_context():
    try:
        print("Testing DB insert into alert_acknowledgments...")
        ack = AlertAcknowledgment(alert_key="test-alert-123", acknowledged_by="Manual Test")
        db.session.add(ack)
        db.session.commit()
        print("SUCCESS! Inserted test-alert-123")
        
        # Now read it back
        res = AlertAcknowledgment.query.filter_by(alert_key="test-alert-123").first()
        if res:
            print(f"Verified: Found {res.alert_key} in DB.")
        else:
            print("ERROR: Could not find the record after commit!")
            
        # Clean up
        db.session.delete(res)
        db.session.commit()
        print("Cleaned up.")
    except Exception as e:
        print(f"CRITICAL DB ERROR: {e}")
