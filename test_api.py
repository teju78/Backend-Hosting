import requests
import json

base_url = "http://localhost:5000/api/clinical"

def test_get(path):
    print(f"Testing GET {path}...")
    try:
        r = requests.get(f"{base_url}{path}")
        print(f"Status: {r.status_code}")
        print(f"Body: {r.text[:300]}...")
    except Exception as e:
        print(f"Error: {e}")

test_get("/alerts/doctor/DR-CLINICAI")
test_get("/safety/status")
