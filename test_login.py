import requests

session = requests.Session()
response = session.post('http://127.0.0.1:5001/login', data={'username': 'admin', 'password': 'password123'})
print("Login status code:", response.status_code)
print("Login URL after post:", response.url)

response = session.get('http://127.0.0.1:5001/advances-loans')
print("Advances page status code:", response.status_code)
if response.status_code != 200:
    print("Advances page content:", response.text)
