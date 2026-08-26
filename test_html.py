import requests

session = requests.Session()
session.post('http://127.0.0.1:5001/login', data={'username': 'admin', 'password': 'password123'})
response = session.get('http://127.0.0.1:5001/advances-loans')
print(response.text)
