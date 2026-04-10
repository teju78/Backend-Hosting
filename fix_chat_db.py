import app
from database import db
from models.chat import ChatMessage
import sys
import os

def fix_chat_table():
    flask_app, socketio = app.create_app()
    with flask_app.app_context():
        print("🛠️ Fixing Chat Messages Table Schema...")
        try:
            # Drop the table to reset the primary key from INT to String(36)
            ChatMessage.__table__.drop(db.engine)
            print("✅ Dropped old chat_messages table.")
        except Exception as e:
            print(f"⚠️ Table drop failed (it may not exist): {e}")
        
        try:
            # Create it with the new schema
            ChatMessage.__table__.create(db.engine)
            print("✅ Created new chat_messages table with UUID primary key.")
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            sys.exit(1)

        db.session.commit()
        print("🚀 Chat Database Schema Refined.")

if __name__ == "__main__":
    fix_chat_table()
