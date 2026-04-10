import os

path = r"e:\ClinicAI\backend\event_listener.py"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 138 (index 137) is "try:"
if "try:" in lines[137] and "existing = None" in lines[128]:
    # Shift everything from 138 onwards
    new_try = "                                                 if not existing:\n"
    lines.insert(137, new_try)
    
    # Indent the original try and its block
    for i in range(138, 175): # from index 138 to 174 (lines 139 to 175)
        lines[i] = "    " + lines[i]
    
    # Add else for existing
    new_else = "                                                 else:\n"
    new_else_msg = "                                                     print(f'ℹ️ Appointment already exists for record {record.id}')\n"
    lines.insert(175, new_else)
    lines.insert(176, new_else_msg)
    
    # Replace the COMMIT at line 178 (now shifted)
    # Actually I'll search for it
    for i in range(170, 190):
        if "db.session.commit()" in lines[i]:
            # Indent it
            lines[i] = "    " + lines[i]

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Successfully patched event_listener.py")
else:
    print(f"FAILED: Line 138 content: {repr(lines[137])}")
