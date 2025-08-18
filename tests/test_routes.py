"""Test main routes."""


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200

    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'version' in data
    assert 'environment' in data
    assert 'python_version' in data
    assert 'system' in data


def test_index_endpoint(client):
    """Test index endpoint."""
    response = client.get('/')
    assert response.status_code == 200

    data = response.get_json()
    assert data['message'] == 'Sub Learning Application'
    assert data['status'] == 'running'
    assert 'endpoints' in data
