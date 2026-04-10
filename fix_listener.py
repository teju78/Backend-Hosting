import os
import re

path = r"e:\ClinicAI\backend\event_listener.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find the misaligned appointment block
# It looks for 'existing = None' followed by 'if slot_str and record:' 
# then 'target_time = ...' and finally 'try:'
pattern = re.compile(r'( +)existing = None\n( +)if slot_str and record:\n( +)target_time = ([^\n]+)\n( +)existing = ([^\n]+)\.first\(\)\n( +)\n( +)try:', re.MULTILINE)

# This is too specific. Let's use a simpler one.
# We want to replace exactly what's between lines 130 and 176.

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line numbers are 1-indexed. Line 130 is index 129.
# We want to replace from index 130 to 175.
new_lines = lines[:137] # Up to line 137 (index 136)
new_lines.append("                                                 if not existing:\n")
new_lines.append("                                                     try:\n")
new_lines.append("                                                         from models import Appointment, Staff\n")
new_lines.append("                                                         active_doc = Staff.query.get(doc_id)\n")
new_lines.append("                                                         if not active_doc:\n")
new_lines.append("                                                             active_doc = Staff(id=doc_id, role='doctor', is_on_duty=True)\n")
new_lines.append("                                                             db.session.add(active_doc)\n")
new_lines.append("                                                         new_appt = Appointment(\n")
new_lines.append("                                                             id=f'AUTO-{str(uuid.uuid4())[:8]}',\n")
new_lines.append("                                                             patient_id=str(record.patient_id),\n")
new_lines.append("                                                             doctor_id=doc_id,\n")
new_lines.append("                                                             triage_id=str(record.id),\n")
new_lines.append("                                                             scheduled_at=target_time,\n")
new_lines.append("                                                             status='scheduled'\n")
new_lines.append("                                                         )\n")
new_lines.append("                                                         db.session.add(new_appt)\n")
new_lines.append("                                                         db.session.commit()\n")
new_lines.append("                                                         print(f'🔥 AUTO-BOOKED')\n")
new_lines.append("                                                     except Exception as e:\n")
new_lines.append("                                                         db.session.rollback()\n")
new_lines.append("                                                         print(f'⚠️ Auto-booking failed: {e}')\n")
new_lines.append("                                                 else:\n")
new_lines.append("                                                     print(f'ℹ️ Appointment exists')\n")
new_lines.extend(lines[176:]) # From line 177 (index 176) onwards

# Wait! This is too dangerous without seeing the exact lines again.
# I'll just use a more robust search and replace in the script.
