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
