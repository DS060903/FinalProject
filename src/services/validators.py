"""Validation utilities."""
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from werkzeug.datastructures import FileStorage
import os


def normalize_email(email):
    """
    Normalize email address: lowercase and strip whitespace.
    
    Args:
        email: Raw email string
    
    Returns:
        Normalized email string
    
    Raises:
        ValueError: If email is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")
    
    email = email.strip().lower()
    
    # Validate email format
    # Skip DNS checking for development (check_deliverability=False)
    # This allows example.com and other test domains
    try:
        validated = validate_email(email, check_deliverability=False)
        return validated.email
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email: {str(e)}")


def validate_time_window(start_dt, end_dt, min_duration_minutes=15):
    """
    Validate that a time window is valid (end > start) and meets minimum duration.
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
        min_duration_minutes: Minimum duration in minutes (default: 15)
    
    Raises:
        ValueError: If end_dt <= start_dt or duration < min_duration_minutes
    """
    if not isinstance(start_dt, datetime) or not isinstance(end_dt, datetime):
        raise ValueError("start_dt and end_dt must be datetime objects")
    
    if end_dt <= start_dt:
        raise ValueError("end_dt must be after start_dt")
    
    # Check minimum duration
    duration = (end_dt - start_dt).total_seconds() / 60  # Convert to minutes
    if duration < min_duration_minutes:
        raise ValueError(f"Booking duration must be at least {min_duration_minutes} minutes")


def validate_booking_request(user, resource, start_dt, end_dt):
    """
    Validate a booking request.
    
    Args:
        user: User object (must be authenticated)
        resource: Resource object
        start_dt: Start datetime
        end_dt: End datetime
    
    Raises:
        ValueError: If validation fails
    """
    from ..models.resource import ResourceStatus
    
    # Check user is authenticated
    if not user or not hasattr(user, 'id'):
        raise ValueError("User must be authenticated to create a booking")
    
    # Check resource is not archived
    if resource.status == ResourceStatus.ARCHIVED:
        raise ValueError("Cannot book archived resources")
    
    # Check capacity
    if resource.capacity <= 0:
        raise ValueError("Resource has no capacity available")
    
    # Validate time window
    validate_time_window(start_dt, end_dt)


def validate_capacity(capacity):
    """
    Validate capacity is non-negative integer.
    
    Args:
        capacity: Capacity value
    
    Raises:
        ValueError: If capacity is negative
    """
    if capacity is None:
        return
    if not isinstance(capacity, int):
        raise ValueError("Capacity must be an integer")
    if capacity < 0:
        raise ValueError("Capacity cannot be negative")


def validate_resource_payload(data):
    """
    Validate resource creation/update payload.
    
    Args:
        data: dict with resource fields
    
    Raises:
        ValueError: With descriptive message if validation fails
    """
    errors = []
    
    # Title validation
    title = data.get('title', '').strip()
    if not title:
        errors.append("Title is required and cannot be empty")
    
    # Capacity validation
    capacity = data.get('capacity')
    if capacity is not None:
        try:
            capacity = int(capacity)
            if capacity < 0:
                errors.append("Capacity must be non-negative")
        except (ValueError, TypeError):
            errors.append("Capacity must be an integer")
    
    # Status validation
    status = data.get('status')
    if status is not None:
        # Handle both enum and string status
        from ..models.resource import ResourceStatus
        if isinstance(status, ResourceStatus):
            # Enum is valid, convert to string for comparison
            status_str = status.value
        else:
            status_str = str(status).lower()
        
        valid_statuses = {'draft', 'published', 'archived'}
        if status_str not in valid_statuses:
            errors.append(f"Status must be one of: {', '.join(valid_statuses)}")
    
    # Category length validation
    category = data.get('category')
    if category and len(category) > 80:
        errors.append("Category must be 80 characters or less")
    
    # Location length validation
    location = data.get('location')
    if location and len(location) > 80:
        errors.append("Location must be 80 characters or less")
    
    if errors:
        raise ValueError("; ".join(errors))


def validate_upload(file_storage, max_size=2 * 1024 * 1024, allowed_extensions=None):
    """
    Validate uploaded file.
    
    Args:
        file_storage: Werkzeug FileStorage object
        max_size: Maximum file size in bytes (default: 2MB)
        allowed_extensions: Set of allowed extensions (default: image extensions)
    
    Raises:
        ValueError: With descriptive message if validation fails
    """
    if allowed_extensions is None:
        allowed_extensions = {'jpg', 'jpeg', 'png', 'webp'}
    
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided")
    
    filename = file_storage.filename
    
    # Check extension
    if '.' not in filename:
        raise ValueError("File must have an extension")
    
    # Block double extensions
    if filename.count('.') > 1:
        raise ValueError("File with double extension not allowed")
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError(f"File extension '{ext}' not allowed. Allowed: {', '.join(allowed_extensions)}")
    
    # Check file size
    # Seek to end to get file size
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise ValueError(f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum ({max_size / 1024 / 1024}MB)")
    
    if file_size == 0:
        raise ValueError("File is empty")


def validate_review_payload(rating, comment):
    """
    Validate review rating and comment.
    
    Args:
        rating: Rating value (must be 1-5)
        comment: Comment text
    
    Returns:
        tuple: (rating, comment) validated and cleaned
    
    Raises:
        ValueError: If validation fails
    """
    if rating not in (1, 2, 3, 4, 5):
        raise ValueError("Rating must be 1..5.")
    
    comment = (comment or "").strip()
    if not comment:
        raise ValueError("Comment required.")
    
    if len(comment) > 1000:
        raise ValueError("Comment too long.")
    
    return rating, comment


def validate_pagination(param, default=1, minv=1, maxv=1000):
    """
    Validate and sanitize pagination parameter.
    
    Args:
        param: Pagination parameter value (from request.args or form)
        default: Default value if param is None or invalid
        minv: Minimum allowed value
        maxv: Maximum allowed value
    
    Returns:
        int: Validated pagination value within bounds
    """
    try:
        v = int(param or default)
        return min(max(v, minv), maxv)
    except (ValueError, TypeError):
        return default


