import requests

patient_id = '7df841eb-089f-4cda-ba13-1017787f2643'
url = f"http://127.0.0.1:8007/medications/{patient_id}"

try:
    resp = requests.get(url)
    print(resp.json())
except Exception as e:
    print(e)
