"""Pytest configuration and fixtures."""
import pytest
from src.app import create_app
from src.models import db
from src.config import TestConfig
from src.data_access.dal import create_user
from src.models.user import UserRole


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app(config_name='testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create CLI test runner."""
    return app.test_cli_runner()


def _get_csrf_token(client, url='/auth/login'):
    """Helper to extract CSRF token from login page."""
    resp = client.get(url)
    if resp.status_code == 200:
        content = resp.data.decode()
        if 'name="csrf_token" value="' in content:
            return content.split('name="csrf_token" value="')[1].split('"')[0]
    return ''


@pytest.fixture
def auth_headers_student(client, app):
    """Create authenticated student user and return headers."""
    with app.app_context():
        user = create_user('smoke_student@example.com', 'Password123!', UserRole.STUDENT)
        csrf_token = _get_csrf_token(client)
        client.post('/auth/login', data={
            'email': 'smoke_student@example.com',
            'password': 'Password123!',
            'csrf_token': csrf_token
        }, follow_redirects=True)
    return {}


@pytest.fixture
def auth_headers_admin(client, app):
    """Create authenticated admin user and return headers."""
    with app.app_context():
        user = create_user('smoke_admin@example.com', 'Password123!', UserRole.ADMIN)
        csrf_token = _get_csrf_token(client)
        client.post('/auth/login', data={
            'email': 'smoke_admin@example.com',
            'password': 'Password123!',
            'csrf_token': csrf_token
        }, follow_redirects=True)
    return {}

