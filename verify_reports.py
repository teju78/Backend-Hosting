import requests
import json

base_url = 'http://localhost:5000/api/reports'

try:
    print("Testing GET /history...")
    r1 = requests.get(f"{base_url}/history")
    print(f"GET History: {r1.status_code}")
    
    print("\nTesting POST /generate...")
    payload = {
        "domain": "Clinical",
        "options": {"heatmaps": True, "demographic": True}
    }
    r2 = requests.post(f"{base_url}/generate", json=payload)
    print(f"POST Generate: {r2.status_code}")
    print(f"POST Body: {r2.text}")
    
    print("\nTesting GET /recommendation...")
    r3 = requests.get(f"{base_url}/recommendation")
    print(f"GET Rec: {r3.status_code}")
    print(f"GET Rec Body: {r3.text}")
except Exception as e:
    print(f"Error: {e}")
