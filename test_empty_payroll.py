import requests

session = requests.Session()
session.post('http://127.0.0.1:5001/login', data={'username': 'admin', 'password': 'password123'})
res = session.post('http://127.0.0.1:5001/payroll/generate/2026/9')
print("Payroll generate status code:", res.status_code)
if res.status_code == 500:
    print(res.text[:1000])
