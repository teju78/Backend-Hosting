
import pymysql
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import re

load_dotenv()

key = b'8-GP0vV7e_f8S-r9L1_6K-8P7J-V4R-2Q-1W-3E-4R='
cipher = Fernet(key)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mediagents_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def clean_and_encrypt(val):
    if not val: return None
    # If it is already a binary blob that looks like Fernet (starts with gAAAA)
    # we don't want to double encrypt if possible.
    # But here we know it looks like "b'Eswar'"
    if isinstance(val, bytes):
        val = val.decode('utf-8', 'ignore')
    
    match = re.match(r"b['\"](.+)['\"]", val)
    if match:
        real_val = match.group(1)
        print(f"Fixing: {val} -> {real_val}")
        return cipher.encrypt(real_val.encode('utf-8'))
    
    # If it's already encrypted correctly, it will be a long string starting with gAAA
    if val.startswith("gAAAA"):
        print(f"Already encrypted: {val[:20]}...")
        return val.encode('utf-8')
        
    print(f"Encrypting plain: {val}")
    return cipher.encrypt(val.encode('utf-8'))

def fix():
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, first_name_enc, last_name_enc, dob_enc FROM patients")
    patients = cursor.fetchall()
    
    for p_id, f_enc, l_enc, d_enc in patients:
        new_f = clean_and_encrypt(f_enc)
        new_l = clean_and_encrypt(l_enc)
        new_d = clean_and_encrypt(d_enc)
        
        cursor.execute(
            "UPDATE patients SET first_name_enc=%s, last_name_enc=%s, dob_enc=%s WHERE id=%s",
            (new_f, new_l, new_d, p_id)
        )
        print(f"Updated patient {p_id}")
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    fix()
