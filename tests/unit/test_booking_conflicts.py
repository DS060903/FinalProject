"""Unit tests for booking conflict detection logic."""
import pytest
from datetime import datetime, timedelta
from src.data_access.dal import create_user, create_resource, create_booking, has_conflict
from src.models.user import UserRole
from src.models.resource import ResourceStatus


@pytest.fixture
def booking_setup(app):
    """Setup data for conflict tests."""
    with app.app_context():
        user = create_user('student@test.com', 'Password123!', UserRole.STUDENT)
        staff = create_user('staff@test.com', 'Password123!', UserRole.STAFF)
        
        resource = create_resource({
            'title': 'Test Room',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'created_by': staff.id
        })
        
        base_time = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
        
        return {
            'user_id': user.id,
            'resource_id': resource.id,
            'base_time': base_time
        }


def test_overlapping_bookings_conflict(booking_setup, app):
    """Test that overlapping bookings are detected as conflicts."""
    with app.app_context():
        data = booking_setup
        
        # Create existing booking: 10:00 - 12:00
        start1 = data['base_time']
        end1 = start1 + timedelta(hours=2)
        create_booking(data['user_id'], data['resource_id'], start1, end1)
        
        # Check overlapping: 11:00 - 13:00 (overlaps)
        start2 = start1 + timedelta(hours=1)
        end2 = start2 + timedelta(hours=2)
        
        assert has_conflict(data['resource_id'], start2, end2) is True


def test_non_overlapping_bookings_no_conflict(booking_setup, app):
    """Test that non-overlapping bookings don't conflict."""
    with app.app_context():
        data = booking_setup
        
        # Create existing booking: 10:00 - 12:00
        start1 = data['base_time']
        end1 = start1 + timedelta(hours=2)
        create_booking(data['user_id'], data['resource_id'], start1, end1)
        
        # Check non-overlapping: 13:00 - 15:00 (no overlap)
        start2 = start1 + timedelta(hours=3)
        end2 = start2 + timedelta(hours=2)
        
        assert has_conflict(data['resource_id'], start2, end2) is False


def test_adjacent_bookings_no_conflict(booking_setup, app):
    """Test that adjacent bookings (end == start) don't conflict."""
    with app.app_context():
        data = booking_setup
        
        # Create existing booking: 10:00 - 12:00
        start1 = data['base_time']
        end1 = start1 + timedelta(hours=2)
        create_booking(data['user_id'], data['resource_id'], start1, end1)
        
        # Check adjacent: 12:00 - 14:00 (no conflict)
        start2 = end1
        end2 = start2 + timedelta(hours=2)
        
        assert has_conflict(data['resource_id'], start2, end2) is False

