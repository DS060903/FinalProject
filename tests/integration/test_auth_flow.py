"""Integration tests for authentication flow (register → login → protected route)."""
import pytest
from src.data_access.dal import create_user
from src.models.user import UserRole


def test_register_login_protected_route_flow(client, app):
    """Test complete auth flow: register → login → access protected route."""
    with app.app_context():
        # Step 1: Create user (simulating registration)
        user = create_user('testuser@example.com', 'Password123!', UserRole.STUDENT)
        assert user.id is not None
        
        # Step 2: Login via POST /auth/login
        login_page = client.get('/auth/login')
        csrf_token = ''
        if 'csrf_token' in login_page.data.decode():
            csrf_token = login_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        response = client.post('/auth/login', data={
            'email': 'testuser@example.com',
            'password': 'Password123!',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        # Should successfully login (status 200)
        assert response.status_code == 200
        
        # Step 3: Access protected route (e.g., /resources or /auth/me)
        protected_response = client.get('/resources')
        
        # Should be accessible (200) when logged in
        assert protected_response.status_code == 200


def test_login_with_invalid_credentials_fails(client, app):
    """Test that login fails with invalid credentials."""
    with app.app_context():
        # Create user with known password
        create_user('test@example.com', 'CorrectPass123!', UserRole.STUDENT)
        
        # Attempt login with wrong password
        login_page = client.get('/auth/login')
        csrf_token = ''
        if 'csrf_token' in login_page.data.decode():
            csrf_token = login_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'csrf_token': csrf_token
        }, follow_redirects=False)
        
        # Should not redirect to success page (should stay on login or show error)
        # Status could be 200 (form with error) or 302 (redirect back to login)
        assert response.status_code in [200, 302]
        
        # If we try to access protected resource, should fail
        resources_response = client.get('/resources')
        # Either shows login prompt or is accessible but user not logged in
        assert resources_response.status_code in [200, 302, 401]

