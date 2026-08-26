import requests
import traceback

session = requests.Session()

def check(url, data=None):
    try:
        if data:
            r = session.post(url, data=data)
        else:
            r = session.get(url)
        print(f"{url} -> {r.status_code}")
        if r.status_code == 500:
            print("500 ERROR ON", url)
            print(r.text[:500])
    except Exception as e:
        print(f"Error on {url}: {e}")

check('http://127.0.0.1:5001/')
check('http://127.0.0.1:5001/login')
check('http://127.0.0.1:5001/login', data={'username': 'admin', 'password': 'password123'})
check('http://127.0.0.1:5001/')
check('http://127.0.0.1:5001/advances-loans')
check('http://127.0.0.1:5001/payroll/dashboard/2026/8')

