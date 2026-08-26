import requests

session = requests.Session()
session.post('http://127.0.0.1:5001/login', data={'username': 'admin', 'password': 'password123'})

# Add a loan and an advance for employee 1
session.post('http://127.0.0.1:5001/advances/new', data={
    'employee_id': 1,
    'amount': 1000,
    'reason': 'test advance'
})
# Approve advance
# We need the advance ID, let's just do it directly in DB for test
import psycopg2
from config import Config
conn = psycopg2.connect(**Config.db_connection_params())
with conn.cursor() as cur:
    cur.execute("UPDATE advances SET status = 'Approved'")
    cur.execute("UPDATE loans SET status = 'Approved'")
conn.commit()

# Trigger payroll generate
res = session.post('http://127.0.0.1:5001/payroll/generate/2026/8')
print("Payroll generate status code:", res.status_code)
if res.status_code == 500:
    print(res.text[:1000])

