"""Unit tests for booking status transitions."""
import pytest
from datetime import datetime, timedelta
from src.data_access.dal import (
    create_user, create_resource, create_booking,
    approve_booking, reject_booking, cancel_booking, complete_booking
)
from src.models.user import UserRole
from src.models.resource import ResourceStatus
from src.models.booking import BookingStatus


@pytest.fixture
def status_setup(app):
    """Setup data for status transition tests."""
    with app.app_context():
        student = create_user('student@test.com', 'Password123!', UserRole.STUDENT)
        staff = create_user('staff@test.com', 'Password123!', UserRole.STAFF)
        admin = create_user('admin@test.com', 'Password123!', UserRole.ADMIN)
        
        resource = create_resource({
            'title': 'Test Room',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'requires_approval': True,
            'created_by': staff.id
        })
        
        return {
            'student_id': student.id,
            'staff_id': staff.id,
            'admin_id': admin.id,
            'resource_id': resource.id
        }


def test_pending_to_approved_transition(status_setup, app):
    """Test valid transition: pending → approved."""
    with app.app_context():
        data = status_setup
        
        start_dt = datetime.utcnow() + timedelta(days=1)
        end_dt = start_dt + timedelta(hours=2)
        
        booking = create_booking(data['student_id'], data['resource_id'], start_dt, end_dt)
        assert booking.status == BookingStatus.PENDING
        
        approved = approve_booking(booking.id, data['staff_id'])
        assert approved.status == BookingStatus.APPROVED


def test_pending_to_rejected_transition(status_setup, app):
    """Test valid transition: pending → rejected."""
    with app.app_context():
        data = status_setup
        
        start_dt = datetime.utcnow() + timedelta(days=2)
        end_dt = start_dt + timedelta(hours=2)
        
        booking = create_booking(data['student_id'], data['resource_id'], start_dt, end_dt)
        assert booking.status == BookingStatus.PENDING
        
        rejected = reject_booking(booking.id, data['staff_id'])
        assert rejected.status == BookingStatus.REJECTED


def test_approved_to_cancelled_transition(status_setup, app):
    """Test valid transition: approved → cancelled."""
    with app.app_context():
        data = status_setup
        
        start_dt = datetime.utcnow() + timedelta(days=3)
        end_dt = start_dt + timedelta(hours=2)
        
        booking = create_booking(data['student_id'], data['resource_id'], start_dt, end_dt)
        approved = approve_booking(booking.id, data['staff_id'])
        assert approved.status == BookingStatus.APPROVED
        
        cancelled = cancel_booking(approved.id, data['student_id'])
        assert cancelled.status == BookingStatus.CANCELLED


def test_approved_to_completed_transition(status_setup, app):
    """Test valid transition: approved → completed."""
    with app.app_context():
        data = status_setup
        
        # Past booking
        start_dt = datetime.utcnow() - timedelta(days=1)
        end_dt = start_dt + timedelta(hours=2)
        
        booking = create_booking(data['student_id'], data['resource_id'], start_dt, end_dt)
        approved = approve_booking(booking.id, data['staff_id'])
        
        completed = complete_booking(approved.id, data['admin_id'])
        assert completed.status == BookingStatus.COMPLETED


def test_invalid_transition_rejected_to_approved_fails(status_setup, app):
    """Test invalid transition: rejected → approved raises error."""
    with app.app_context():
        data = status_setup
        
        start_dt = datetime.utcnow() + timedelta(days=4)
        end_dt = start_dt + timedelta(hours=2)
        
        booking = create_booking(data['student_id'], data['resource_id'], start_dt, end_dt)
        rejected = reject_booking(booking.id, data['staff_id'])
        
        # Try to approve a rejected booking - should fail
        with pytest.raises(ValueError, match="Cannot approve"):
            approve_booking(rejected.id, data['staff_id'])

