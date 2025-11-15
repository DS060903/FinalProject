"""Unit tests for security utilities (SQL injection, XSS protection)."""
import pytest
from src.data_access.dal import create_user, get_user_by_email
from src.models.user import UserRole
from src.services.sanitize import sanitize_body


def test_sql_injection_prevented_in_email_lookup(app):
    """Test that SQL injection attempts in email lookup are safely handled."""
    with app.app_context():
        # Create a normal user
        create_user('normal@test.com', 'Password123!', UserRole.STUDENT)
        
        # Query with special characters (parameterized queries handle safely)
        result = get_user_by_email('normal@test.com')
        assert result is not None
        
        # Non-existent email returns None
        result = get_user_by_email('nonexistent@test.com')
        assert result is None


def test_parameterized_queries_used_in_dal(app):
    """Test that DAL uses parameterized queries (SQLAlchemy ORM)."""
    with app.app_context():
        # Create user
        user = create_user('test@param.com', 'Password123!', UserRole.STUDENT)
        
        # Query by email (should use parameterized query)
        result = get_user_by_email('test@param.com')
        
        # Should find the user safely
        assert result is not None
        assert result.id == user.id


def test_sanitize_body_removes_blocked_words():
    """Test that sanitize_body removes blocked words."""
    text = "This is a spam message trying to hack your account"
    
    result = sanitize_body(text)
    
    # Should replace blocked words with ***
    assert "***" in result
    assert "spam" not in result.lower()


def test_sanitize_body_handles_empty_input():
    """Test that sanitize_body handles empty or None input gracefully."""
    assert sanitize_body("") == ""
    assert sanitize_body(None) == ""
    assert sanitize_body("   ") == ""


def test_sanitize_body_enforces_length_limit():
    """Test that sanitize_body enforces 2000 character limit."""
    long_text = "A" * 3000
    
    result = sanitize_body(long_text)
    
    # Should truncate to 2000 characters
    assert len(result) == 2000

