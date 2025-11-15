"""Unit tests for DAL CRUD operations (independent of Flask routes)."""
import pytest
from src.data_access.dal import (
    create_user, get_user_by_email,
    create_resource, list_resources, get_resource, update_resource,
    create_booking, list_bookings_for_user
)
from src.models.user import UserRole
from src.models.resource import ResourceStatus
from datetime import datetime, timedelta


def test_create_user_dal(app):
    """Test user creation via DAL."""
    with app.app_context():
        user = create_user('test@example.com', 'Password123!', UserRole.STUDENT)
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.role == UserRole.STUDENT
        assert user.password_hash != 'Password123!'  # Should be hashed


def test_get_user_by_email_dal(app):
    """Test retrieving user by email via DAL."""
    with app.app_context():
        create_user('test@example.com', 'Password123!', UserRole.STUDENT)
        user = get_user_by_email('test@example.com')
        assert user is not None
        assert user.email == 'test@example.com'


def test_create_resource_dal(app):
    """Test resource creation via DAL."""
    with app.app_context():
        user = create_user('staff@example.com', 'Password123!', UserRole.STAFF)
        
        resource = create_resource({
            'title': 'Test Room',
            'description': 'A test room',
            'category': 'Room',
            'location': 'Building 1',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': user.id
        })
        
        assert resource.id is not None
        assert resource.title == 'Test Room'
        assert resource.capacity == 10


def test_list_resources_dal(app):
    """Test listing resources via DAL."""
    with app.app_context():
        user = create_user('staff@example.com', 'Password123!', UserRole.STAFF)
        
        create_resource({
            'title': 'Room 1',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': user.id
        })
        
        create_resource({
            'title': 'Room 2',
            'capacity': 20,
            'status': ResourceStatus.PUBLISHED,
            'created_by': user.id
        })
        
        resources = list_resources({}).all()
        assert len(resources) >= 2


def test_update_resource_dal(app):
    """Test updating resource via DAL."""
    with app.app_context():
        user = create_user('staff@example.com', 'Password123!', UserRole.STAFF)
        
        resource = create_resource({
            'title': 'Original Title',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': user.id
        })
        
        updated = update_resource(resource.id, {
            'title': 'Updated Title',
            'capacity': 20
        })
        
        assert updated.title == 'Updated Title'
        assert updated.capacity == 20


def test_create_booking_dal(app):
    """Test booking creation via DAL."""
    with app.app_context():
        student = create_user('student@example.com', 'Password123!', UserRole.STUDENT)
        staff = create_user('staff@example.com', 'Password123!', UserRole.STAFF)
        
        resource = create_resource({
            'title': 'Test Room',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': staff.id
        })
        
        start_dt = datetime.utcnow() + timedelta(days=1)
        end_dt = start_dt + timedelta(hours=2)
        
        booking = create_booking(student.id, resource.id, start_dt, end_dt)
        
        assert booking.id is not None
        assert booking.user_id == student.id
        assert booking.resource_id == resource.id


def test_list_bookings_for_user_dal(app):
    """Test listing user bookings via DAL."""
    with app.app_context():
        student = create_user('student@example.com', 'Password123!', UserRole.STUDENT)
        staff = create_user('staff@example.com', 'Password123!', UserRole.STAFF)
        
        resource = create_resource({
            'title': 'Test Room',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': staff.id
        })
        
        start_dt = datetime.utcnow() + timedelta(days=1)
        end_dt = start_dt + timedelta(hours=2)
        
        create_booking(student.id, resource.id, start_dt, end_dt)
        
        bookings = list_bookings_for_user(student.id).all()
        assert len(bookings) >= 1
        assert bookings[0].user_id == student.id

