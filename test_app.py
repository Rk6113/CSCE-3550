import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_jwks_endpoint(client):
    response = client.get('/jwks')
    assert response.status_code == 200
    data = response.get_json()
    assert 'keys' in data

def test_auth_endpoint(client):
    response = client.post('/auth')
    assert response.status_code == 200
    data = response.get_json()
    assert 'token' in data

def test_auth_expired_endpoint(client):
    response = client.post('/auth?expired=true')
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.get_json()
        assert 'token' in data
    else:
        data = response.get_json()
        assert 'message' in data
