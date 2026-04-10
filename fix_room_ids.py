from app import create_app
from database import db
from models.appointment import Appointment
from models.room import Room

def fix():
    app, _ = create_app()
    with app.app_context():
        # Fetch all active rooms
        rooms = db.session.query(Room).filter(Room.is_active == True).all()
        if not rooms:
            print("No active rooms found.")
            return
            
        # Fetch appointments with NULL room_id
        appts = db.session.query(Appointment).filter(Appointment.room_id == None).all()
        print(f"Found {len(appts)} appointments with missing room IDs.")
        
        for i, a in enumerate(appts):
            # Assign room in round-robin fashion
            room = rooms[i % len(rooms)]
            a.room_id = room.id
            print(f"Mapping Appt {a.id} -> Room {room.name}")
            
        db.session.commit()
        print("✅ Logistical Recovery Complete. All sessions indexed to room shards.")

if __name__ == "__main__":
    fix()
