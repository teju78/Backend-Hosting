from app import create_app
from database import db
from models.room import Room

def seed():
    app, _ = create_app()
    with app.app_context():
        # Check if rooms exist
        if db.session.query(Room).count() == 0:
            rooms = [
                Room(name="Consultation A-101", type="consultation", is_active=True, equipment={"stethoscope": True, "pc": True}),
                Room(name="Pediatrics B-205", type="consultation", is_active=True, equipment={"toys": True}),
                Room(name="Emergency Bay 1", type="emergency", is_active=True, equipment={"ventilator": True}),
                Room(name="Dental Suite 1", type="procedure", is_active=True, equipment={"chair": True}),
                Room(name="Diagnostic Lab", type="procedure", is_active=False, equipment={"xray": False}),
            ]
            db.session.add_all(rooms)
            db.session.commit()
            print("✅ Clinical Room Shards Seeded.")
        else:
            print("Rooms already indexed.")

if __name__ == "__main__":
    seed()
