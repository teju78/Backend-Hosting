from app import create_app
from database import db
import sys

app, _ = create_app()
with app.app_context():
    try:
        db.create_all()
        print("Successfully recreated all tables.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
