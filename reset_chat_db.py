from app import create_app
from database import db
from sqlalchemy import text

app, _ = create_app()
with app.app_context():
    try:
        # Drop and recreate the chat_messages table to apply PK change
        # SQLite doesn't support easy ALTER TABLE for PKs
        # But since we use MySQL, we can just drop it
        db.session.execute(text("DROP TABLE IF EXISTS chat_messages"))
        db.session.commit()
        db.create_all()
        print("Successfully reset chat_messages table with Integer PK.")
    except Exception as e:
        print(f"Error resetting table: {e}")
