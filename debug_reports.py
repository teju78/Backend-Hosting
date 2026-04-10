import os
import sys

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from app import create_app
from database import db
from models.report import GeneratedReport

app, _ = create_app()
with app.app_context():
    try:
        # Check if table exists
        db.create_all()
        count = GeneratedReport.query.count()
        print(f"DEBUG: Found {count} reports")
    except Exception as e:
        import traceback
        print(f"DEBUG ERROR: {str(e)}")
        traceback.print_exc()
