import sqlite3
import os

path = os.path.join("instance", "clinicai.db")
if os.path.exists(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("UPDATE triage_records SET decision_support = NULL")
    conn.commit()
    print("Cleared cache!")
else:
    print(f"DB not found at {path}")
