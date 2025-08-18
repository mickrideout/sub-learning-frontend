"""Test error handlers."""


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