from app import create_app
from database import db
from models.staff import Staff
from models.room import Room
import json

def check():
    app, _ = create_app()
    with app.app_context():
        staff = db.session.query(Staff).all()
        rooms = db.session.query(Room).all()
        print(f"STAFF_COUNT:{len(staff)}")
        print(f"ROOM_COUNT:{len(rooms)}")
        for s in staff:
            print(f"STAFF_NAME:{s.first_name} {s.last_name} ROLE:{s.role}")
        for r in rooms:
            print(f"ROOM_NAME:{r.name} TYPE:{r.type}")

if __name__ == "__main__":
    check()
