from app import create_app
from database import db
from models import Notification
import uuid

app, _ = create_app()
with app.app_context():
    try:
        # Check if table exists
        db.session.execute(db.text("SELECT * FROM notifications LIMIT 1"))
        print("✅ Notifications table exists and is accessible.")
        
        # Test query
        notifs = Notification.query.all()
        print(f"✅ Found {len(notifs)} notifications.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
