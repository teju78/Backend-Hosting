import requests
try:
    r = requests.get('http://localhost:5000/api/reports/history')
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text}")
except Exception as e:
    print(f"Error: {e}")
