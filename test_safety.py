import requests

try:
    print("Testing GET /api/clinical/safety/status")
    r = requests.get('http://localhost:5000/api/clinical/safety/status')
    print("Status:", r.status_code)
    try:
        print("Result:", r.json())
    except:
        print("Raw Content:", r.text)
except Exception as e:
    print("Error:", e)
