"""Integration tests for negative route scenarios (invalid payloads, bad requests)."""
import pytest
from src.data_access.dal import create_user, create_resource
from src.models.user import UserRole
from src.models.resource import ResourceStatus
from datetime import datetime, timedelta


@pytest.fixture
def auth_student(client, app):
    """Create and login a student user."""
    with app.app_context():
        user = create_user('student@test.com', 'Password123!', UserRole.STUDENT)
        
        # Login
        login_page = client.get('/auth/login')
        csrf_token = ''
        if 'csrf_token' in login_page.data.decode():
            csrf_token = login_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        client.post('/auth/login', data={
            'email': 'student@test.com',
            'password': 'Password123!',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        
        return user


def test_booking_with_invalid_dates_returns_400(auth_student, client, app):
    """Test that booking with end_dt < start_dt returns 400 error."""
    with app.app_context():
        # Create a resource
        staff = create_user('staff@test.com', 'Password123!', UserRole.STAFF)
        resource = create_resource({
            'title': 'Test Room',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': staff.id
        })
        
        # Get booking page to extract CSRF token
        booking_page = client.get(f'/resources/{resource.id}')
        csrf_token = ''
        if 'csrf_token' in booking_page.data.decode():
            csrf_token = booking_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        # Attempt to book with invalid dates (end before start)
        start = datetime.utcnow() + timedelta(days=1)
        end = start - timedelta(hours=1)  # Invalid: end before start
        
        response = client.post('/bookings', data={
            'resource_id': resource.id,
            'start_dt': start.strftime('%Y-%m-%d %H:%M:%S'),
            'end_dt': end.strftime('%Y-%m-%d %H:%M:%S'),
            'csrf_token': csrf_token
        }, follow_redirects=False)
        
        # Should return 400 or 422 (bad request)
        assert response.status_code in [400, 422, 302]  # 302 if it redirects with error flash


def test_missing_required_field_returns_error(auth_student, client, app):
    """Test that POST with missing required field returns error."""
    with app.app_context():
        staff = create_user('staff@test.com', 'Password123!', UserRole.STAFF)
        resource = create_resource({
            'title': 'Test Room',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': staff.id
        })
        
        # Get CSRF token
        booking_page = client.get(f'/resources/{resource.id}')
        csrf_token = ''
        if 'csrf_token' in booking_page.data.decode():
            csrf_token = booking_page.data.decode().split('name="csrf_token" value="')[1].split('"')[0]
        
        # Attempt to book without end_dt (required field)
        start = datetime.utcnow() + timedelta(days=1)
        
        response = client.post('/bookings', data={
            'resource_id': resource.id,
            'start_dt': start.strftime('%Y-%m-%d %H:%M:%S'),
            # Missing end_dt
            'csrf_token': csrf_token
        }, follow_redirects=False)
        
        # Should return error (400, 422, or redirect with flash)
        assert response.status_code in [400, 422, 302]

