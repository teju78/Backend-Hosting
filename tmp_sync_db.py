import os
import sys

# Add the current directory to sys.path to allow imports
sys.path.append(os.getcwd())

from app import create_app
from database import db

def force_db_creation():
    app, _ = create_app()
    with app.app_context():
        db.create_all()
        print("Done: Tables created or confirmed.")

if __name__ == "__main__":
    force_db_creation()
