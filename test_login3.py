import requests

session = requests.Session()
response = session.post('http://127.0.0.1:5001/login', data={'username': 'admin', 'password': 'password123'})
print("Login URL:", response.url)
print("Login status code:", response.status_code)

response = session.get('http://127.0.0.1:5001/advances-loans')
print("Advances page URL:", response.url)
print("Advances page status code:", response.status_code)
