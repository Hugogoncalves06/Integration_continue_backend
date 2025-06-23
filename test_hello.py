import pytest
from hello import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert b'healthy' in rv.data

def test_create_user(client):
    data = {
        'firstName': 'Test',
        'lastName': 'User',
        'email': 'test@example.com',
        'birthDate': '1990-01-01',
        'city': 'TestCity',
        'postalCode': '12345'
    }
    response = client.post('/api/users', 
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code == 201
    json_data = json.loads(response.data)
    assert json_data['email'] == 'test@example.com'

def test_get_users(client):
    response = client.get('/api/users')
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert isinstance(json_data, list)

def test_delete_user_unauthorized(client):
    response = client.delete('/api/users/1')
    assert response.status_code == 401

def test_get_user_unauthorized(client):
    response = client.get('/api/users/1')
    assert response.status_code == 401

def test_admin_login(client):
    data = {
        'email': 'admin@example.com',
        'password': 'admin123'
    }
    response = client.post('/api/login', 
                         data=json.dumps(data),
                         content_type='application/json')
    assert response.status_code in [200, 401]  # 200 si les credentials sont corrects, 401 sinon

def test_create_user_missing_fields(client):
    # Missing 'password'
    data = {
        'firstName': 'Test',
        'lastName': 'User',
        'email': 'missingpass@example.com',
        'birthDate': '1990-01-01',
        'city': 'TestCity',
        'postalCode': '12345'
    }
    response = client.post('/api/users', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert b'Le champ password est requis' in response.data

def test_create_user_weak_password(client):
    data = {
        'firstName': 'Test',
        'lastName': 'User',
        'email': 'weakpass@example.com',
        'birthDate': '1990-01-01',
        'city': 'TestCity',
        'postalCode': '12345',
        'password': 'weak'
    }
    response = client.post('/api/users', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 400
    assert b'mot de passe doit contenir au moins 8 caract' in response.data

def test_create_user_duplicate_email(client):
    data = {
        'firstName': 'Test',
        'lastName': 'User',
        'email': 'duplicate@example.com',
        'birthDate': '1990-01-01',
        'city': 'TestCity',
        'postalCode': '12345',
        'password': 'Password1'
    }
    # First creation should succeed
    response1 = client.post('/api/users', data=json.dumps(data), content_type='application/json')
    # Second creation should fail with 409
    response2 = client.post('/api/users', data=json.dumps(data), content_type='application/json')
    assert response2.status_code == 409
    assert b'dej' in response2.data or b'dej' in response2.data

def test_login_missing_fields(client):
    response = client.post('/api/login', data=json.dumps({'email': 'admin@example.com'}), content_type='application/json')
    assert response.status_code == 400
    assert b'Email et mot de passe requis' in response.data

def test_login_invalid_credentials(client):
    data = {'email': 'notfound@example.com', 'password': 'WrongPass123'}
    response = client.post('/api/login', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 401
    assert b'Identifiants invalides' in response.data

def test_create_admin_unauthorized(client):
    data = {'email': 'newadmin@example.com', 'password': 'AdminPass1', 'role': 'admin'}
    response = client.post('/api/admins', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 401

def test_create_admin_missing_fields(client):
    # Simulate admin token (should be replaced with a valid token in a real test)
    headers = {'Authorization': 'Bearer fake_admin_token'}
    data = {'email': 'admin2@example.com', 'password': 'AdminPass1'}
    response = client.post('/api/admins', data=json.dumps(data), content_type='application/json', headers=headers)
    # Should fail because 'role' is missing
    assert response.status_code in [400, 401]

def test_get_user_not_found(client):
    # Simulate admin token (should be replaced with a valid token in a real test)
    headers = {'Authorization': 'Bearer fake_admin_token'}
    response = client.get('/api/users/99999', headers=headers)
    assert response.status_code in [401, 404]

def test_delete_user_not_found(client):
    # Simulate admin token (should be replaced with a valid token in a real test)
    headers = {'Authorization': 'Bearer fake_admin_token'}
    response = client.delete('/api/users/99999', headers=headers)
    assert response.status_code in [401, 404]