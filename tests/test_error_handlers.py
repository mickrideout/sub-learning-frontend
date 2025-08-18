"""Test error handlers."""
from unittest.mock import patch


def test_404_api_error(client):
    """Test 404 error for API routes returns JSON."""
    response = client.get('/api/nonexistent')
    assert response.status_code == 404
    
    data = response.get_json()
    assert data['error'] == 'Resource not found'
    assert data['code'] == 'not_found'


def test_404_html_error(client):
    """Test 404 error for regular routes returns HTML."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    assert 'text/html' in response.content_type


def test_health_endpoint_exception_handling(client):
    """Test health endpoint handles exceptions gracefully."""
    with patch('app.blueprints.main.routes.sys.version', side_effect=Exception("Mock error")):
        response = client.get('/health')
        assert response.status_code == 500
        
        data = response.get_json()
        assert data['error'] == 'Health check failed'
        assert data['code'] == 'health_check_error'
        assert 'timestamp' in data


def test_json_request_error_handling(client):
    """Test JSON requests get JSON error responses."""
    response = client.get('/nonexistent', headers={'Content-Type': 'application/json'})
    assert response.status_code == 404
    assert response.is_json
    
    data = response.get_json()
    assert data['error'] == 'Resource not found'
    assert data['code'] == 'not_found'