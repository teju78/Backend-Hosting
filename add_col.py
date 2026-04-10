import sqlite3
try:
    conn = sqlite3.connect("clinicai.db")
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE triage_records ADD COLUMN risk_analysis JSON;")
    conn.commit()
    print("Added column risk_analysis")
except Exception as e:
    print(f"Passed/Ignored: {e}")
finally:
    conn.close()
