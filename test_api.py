import requests
import json

BASE_URL = 'http://localhost:5000'

def test_registration():
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    response = requests.post(f'{BASE_URL}/auth/signup', json=data)
    print(f'Registration: {response.status_code}')
    print(response.json())
    return response.json() if response.status_code == 201 else None

def test_login():
    data = {
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=data)
    print(f'Login: {response.status_code}')
    print(response.json())
    return response.json() if response.status_code == 200 else None

def test_analyze_text(token):
    headers = {'Authorization': f'Bearer {token}'}
    data = {'text': 'This is a test news article about politics and current events.'}
    response = requests.post(f'{BASE_URL}/analyzeText', json=data, headers=headers)
    print(f'Analyze Text: {response.status_code}')
    print(response.json())
    return response

if __name__ == '__main__':
    print("Testing API endpoints...")

    # Test registration
    reg_result = test_registration()

    # Test login
    login_result = test_login()
    if login_result and 'token' in login_result:
        token = login_result['token']
        print(f"Got token: {token[:20]}...")

        # Test analysis
        test_analyze_text(token)
    else:
        print("Login failed")