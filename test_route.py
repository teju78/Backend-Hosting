import requests

try:
    print("Testing GET /api/clinical/triage/feed")
    r = requests.get('http://localhost:5000/api/clinical/triage/feed')
    print("GET Status:", r.status_code)
    print("GET Result:", r.json())

    print("\nTesting POST /api/clinical/triage/test")
    r = requests.post('http://localhost:5000/api/clinical/triage/test')
    print("POST Status:", r.status_code)
    print("POST Result:", r.json())
except Exception as e:
    print("Error:", e)
