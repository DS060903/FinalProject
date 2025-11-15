"""Unit tests for validation utility functions."""
import pytest
from src.services.validators import validate_pagination, validate_time_window
from datetime import datetime, timedelta


def test_validate_pagination_normal():
    """Test that validate_pagination returns correct integer for valid input."""
    assert validate_pagination("5") == 5
    assert validate_pagination("10") == 10
    assert validate_pagination("1") == 1


def test_validate_pagination_bounds():
    """Test that validate_pagination enforces min/max bounds."""
    # Test max bound (1000)
    assert validate_pagination("99999") == 1000
    
    # Test min bound (1)
    assert validate_pagination("-5") == 1
    assert validate_pagination("0") == 1


def test_validate_pagination_invalid_type():
    """Test that validate_pagination handles invalid types gracefully."""
    # Invalid string → should return default (1)
    assert validate_pagination("abc") == 1
    
    # None → should return default (1)
    assert validate_pagination(None) == 1


def test_validate_time_window_valid():
    """Test that validate_time_window accepts valid time windows."""
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(hours=2)
    
    # Should not raise any exception
    validate_time_window(start, end)


def test_validate_time_window_invalid_end_before_start():
    """Test that validate_time_window rejects end < start."""
    start = datetime.utcnow() + timedelta(days=1)
    end = start - timedelta(hours=1)  # End before start
    
    with pytest.raises(ValueError, match="end_dt must be after start_dt"):
        validate_time_window(start, end)


def test_validate_time_window_same_time():
    """Test that validate_time_window rejects end == start."""
    start = datetime.utcnow() + timedelta(days=1)
    end = start  # Same time
    
    with pytest.raises(ValueError, match="end_dt must be after start_dt"):
        validate_time_window(start, end)


def test_validate_time_window_minimum_duration():
    """Test that validate_time_window enforces minimum duration (15 minutes)."""
    start = datetime.utcnow() + timedelta(days=1)
    end = start + timedelta(minutes=10)  # Only 10 minutes
    
    with pytest.raises(ValueError, match="Booking duration must be at least 15 minutes"):
        validate_time_window(start, end, min_duration_minutes=15)

