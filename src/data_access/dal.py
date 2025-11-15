"""Data Access Layer - all database operations go through here.

Controllers must use these functions and never directly access db.session or models.
"""
from datetime import datetime
from sqlalchemy import and_, or_
from ..models import db, User, Resource, Booking, Message, Review
from ..models.user import UserRole
from ..models.resource import ResourceStatus
from ..models.booking import BookingStatus
import bcrypt


# ============================================================================
# User Operations
# ============================================================================

def create_user(email, raw_password, role=UserRole.STUDENT):
    """
    Create a new user with hashed password.
    
    Args:
        email: User email (will be normalized)
        raw_password: Plain text password (will be hashed)
        role: UserRole enum (default: STUDENT)
    
    Returns:
        User instance
    
    Raises:
        ValueError: If email already exists or password is invalid
    """
    from ..services.validators import normalize_email
    
    normalized_email = normalize_email(email)
    
    # Check if user exists
    if get_user_by_email(normalized_email):
        raise ValueError(f"User with email {normalized_email} already exists")
    
    # Validate password strength
    if len(raw_password) < 8:
        raise ValueError("Password must be at least 8 characters")
    
    # Check for at least one uppercase letter
    if not any(c.isupper() for c in raw_password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    # Check for at least one lowercase letter
    if not any(c.islower() for c in raw_password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    # Check for at least one digit
    if not any(c.isdigit() for c in raw_password):
        raise ValueError("Password must contain at least one number")
    
    # Check for at least one special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in raw_password):
        raise ValueError("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
    
    # Hash password
    password_hash = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user = User(
        email=normalized_email,
        password_hash=password_hash,
        role=role
    )
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email):
    """
    Get user by email (case-insensitive).
    
    Args:
        email: Email address
    
    Returns:
        User instance or None
    """
    from ..services.validators import normalize_email
    
    normalized_email = normalize_email(email)
    return User.query.filter_by(email=normalized_email).first()


def get_user(user_id):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
    
    Returns:
        User instance or None
    """
    return User.query.get(user_id)


# ============================================================================
# Resource Operations
# ============================================================================

def create_resource(data):
    """
    Create a new resource.
    
    Args:
        data: dict with keys: title, description, category, location, capacity,
              status, availability_rules, created_by
    
    Returns:
        Resource instance
    """
    from ..services.validators import validate_resource_payload, validate_capacity
    
    # Validate payload
    validate_resource_payload(data)
    
    if 'capacity' in data:
        validate_capacity(data['capacity'])
    
    resource = Resource(
        title=data['title'],
        description=data.get('description'),
        category=data.get('category'),
        location=data.get('location'),
        capacity=data.get('capacity', 0),
        status=data.get('status', ResourceStatus.DRAFT),
        requires_approval=data.get('requires_approval', False),
        created_by=data['created_by']
    )
    
    if 'availability_rules' in data:
        resource.set_availability_rules(data['availability_rules'])
    
    db.session.add(resource)
    db.session.commit()
    return resource


def list_resources(filters=None):
    """
    List resources with optional filters.
    
    Args:
        filters: dict with search parameters (see services/search.py)
    
    Returns:
        Query object (can be further filtered/paginated)
    """
    from ..services.search import apply_resource_filters
    
    query = Resource.query
    
    if filters:
        query = apply_resource_filters(query, filters)
    else:
        # Default: only published resources
        query = query.filter(Resource.status == ResourceStatus.PUBLISHED)
    
    return query


def get_resource(resource_id):
    """
    Get a resource by ID.
    
    Args:
        resource_id: Resource ID
    
    Returns:
        Resource instance or None
    """
    return Resource.query.get(resource_id)


def update_resource(resource_id, data):
    """
    Update a resource.
    
    Args:
        resource_id: Resource ID
        data: dict with fields to update
    
    Returns:
        Updated Resource instance
    
    Raises:
        ValueError: If resource not found
    """
    from ..services.validators import validate_resource_payload, validate_capacity
    
    resource = get_resource(resource_id)
    if not resource:
        raise ValueError(f"Resource {resource_id} not found")
    
    # Merge existing data with updates for validation
    validation_data = {
        'title': data.get('title', resource.title),
        'category': data.get('category', resource.category),
        'location': data.get('location', resource.location),
        'capacity': data.get('capacity', resource.capacity),
        'status': data.get('status', resource.status.value if resource.status else None)
    }
    
    # Validate payload
    validate_resource_payload(validation_data)
    
    if 'capacity' in data:
        validate_capacity(data['capacity'])
    
    if 'title' in data:
        resource.title = data['title']
    if 'description' in data:
        resource.description = data['description']
    if 'category' in data:
        resource.category = data['category']
    if 'location' in data:
        resource.location = data['location']
    if 'capacity' in data:
        resource.capacity = data['capacity']
    if 'status' in data:
        resource.status = data['status']
    if 'availability_rules' in data:
        resource.set_availability_rules(data['availability_rules'])
    
    resource.updated_at = datetime.utcnow()
    db.session.commit()
    return resource


def archive_resource(resource_id):
    """
    Archive a resource (set status to ARCHIVED).
    
    Args:
        resource_id: Resource ID
    
    Returns:
        Updated Resource instance
    
    Raises:
        ValueError: If resource not found
    """
    return update_resource(resource_id, {'status': ResourceStatus.ARCHIVED})


def unarchive_resource(resource_id):
    """
    Unarchive a resource (set status to PUBLISHED).
    
    Args:
        resource_id: Resource ID
    
    Returns:
        Updated Resource instance
    
    Raises:
        ValueError: If resource not found
    """
    return update_resource(resource_id, {'status': ResourceStatus.PUBLISHED})


def add_resource_images(resource_id, files):
    """
    Add images to a resource.
    
    Args:
        resource_id: Resource ID
        files: List of Werkzeug FileStorage objects
    
    Returns:
        List of relative paths to stored images
    
    Raises:
        ValueError: If resource not found or validation fails
    """
    from ..services.validators import validate_upload
    from ..services.image_utils import save_uploaded_image
    from flask import current_app
    import os
    
    resource = get_resource(resource_id)
    if not resource:
        raise ValueError(f"Resource {resource_id} not found")
    
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'jpg', 'jpeg', 'png', 'webp'})
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 2 * 1024 * 1024)
    
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)
    
    stored_paths = []
    
    for file_storage in files:
        if not file_storage or not file_storage.filename:
            continue
        
        # Validate upload
        try:
            validate_upload(file_storage, max_size, allowed_extensions)
        except ValueError as e:
            raise ValueError(f"Upload validation failed: {str(e)}")
        
        # Save image and generate thumbnail
        try:
            relative_path, thumbnail_path = save_uploaded_image(
                file_storage, resource_id, upload_folder, allowed_extensions
            )
            stored_paths.append(relative_path)
            current_app.logger.info(f"Successfully saved image: {relative_path}")
        except Exception as e:
            # If one file fails, log and re-raise with context
            import traceback
            current_app.logger.error(f"Failed to save image {file_storage.filename}: {str(e)}\n{traceback.format_exc()}")
            raise ValueError(f"Failed to save image '{file_storage.filename}': {str(e)}")
    
    # Update resource images JSON
    current_images = resource.get_images()
    current_images.extend(stored_paths)
    resource.set_images(current_images)
    resource.updated_at = datetime.utcnow()
    db.session.commit()
    
    return stored_paths


def remove_resource_image(resource_id, relative_path):
    """
    Remove an image from a resource.
    
    Args:
        resource_id: Resource ID
        relative_path: Relative path to image (from static/uploads/resources/)
    
    Returns:
        bool: True if successful
    
    Raises:
        ValueError: If resource not found or image not in resource's images
    """
    from flask import current_app
    from pathlib import Path
    import os
    
    resource = get_resource(resource_id)
    if not resource:
        raise ValueError(f"Resource {resource_id} not found")
    
    current_images = resource.get_images()
    
    if relative_path not in current_images:
        raise ValueError(f"Image {relative_path} not found in resource images")
    
    # Remove from list
    current_images.remove(relative_path)
    resource.set_images(current_images)
    
    # Delete files from filesystem
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    base_path = Path(upload_folder)
    
    # Construct full paths
    full_image_path = base_path / relative_path
    # Find thumbnail (replace filename with _thumb version)
    image_dir = full_image_path.parent
    image_filename = full_image_path.name
    if '.' in image_filename:
        name_part, ext = image_filename.rsplit('.', 1)
        thumbnail_filename = f"{name_part}_thumb.{ext}"
        full_thumbnail_path = image_dir / thumbnail_filename
    else:
        full_thumbnail_path = None
    
    # Delete files if they exist
    try:
        if full_image_path.exists():
            full_image_path.unlink()
        if full_thumbnail_path and full_thumbnail_path.exists():
            full_thumbnail_path.unlink()
    except Exception as e:
        # Log error but continue - image removed from DB even if file delete fails
        pass
    
    resource.updated_at = datetime.utcnow()
    db.session.commit()
    
    return True


# ============================================================================
# Booking Operations
# ============================================================================

def has_conflict(resource_id, start_dt, end_dt, exclude_booking_id=None, include_completed=False):
    """
    Check if a booking time window conflicts with existing bookings.
    
    Strict overlap logic: two bookings conflict if they share any time.
    Adjacent bookings (end == start) do NOT conflict.
    
    Args:
        resource_id: Resource ID
        start_dt: Start datetime
        end_dt: End datetime
        exclude_booking_id: Optional booking ID to exclude from conflict check
        include_completed: If True, also check completed bookings (default: False)
    
    Returns:
        True if conflict exists, False otherwise
    
    Raises:
        ValueError: If end_dt <= start_dt
    """
    from ..services.validators import validate_time_window
    
    validate_time_window(start_dt, end_dt)
    
    # Statuses to check for conflicts
    conflict_statuses = [BookingStatus.APPROVED, BookingStatus.PENDING]
    if include_completed:
        conflict_statuses.append(BookingStatus.COMPLETED)
    
    # Query for overlapping bookings
    # Overlap condition: (start_dt < existing.end_dt) AND (end_dt > existing.start_dt)
    # This excludes adjacent bookings (end == start)
    query = Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.status.in_(conflict_statuses),
        Booking.start_dt < end_dt,
        Booking.end_dt > start_dt
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.first() is not None


def find_conflicts(resource_id, start_dt, end_dt, exclude_booking_id=None):
    """
    Find all bookings that conflict with the given time window.
    
    Args:
        resource_id: Resource ID
        start_dt: Start datetime
        end_dt: End datetime
        exclude_booking_id: Optional booking ID to exclude from conflict check
    
    Returns:
        List of conflicting Booking instances
    """
    from ..services.validators import validate_time_window
    
    validate_time_window(start_dt, end_dt)
    
    # Query for overlapping bookings (approved, pending, completed)
    query = Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.status.in_([BookingStatus.APPROVED, BookingStatus.PENDING, BookingStatus.COMPLETED]),
        Booking.start_dt < end_dt,
        Booking.end_dt > start_dt
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    return query.all()


def create_booking(user_id, resource_id, start_dt, end_dt):
    """
    Create a new booking with approval workflow.
    
    Args:
        user_id: User ID
        resource_id: Resource ID
        start_dt: Start datetime
        end_dt: End datetime
    
    Returns:
        Booking instance
    
    Raises:
        ValueError: If validation fails, conflict exists, or resource not found
    """
    from ..services.validators import validate_booking_request
    from ..models import User
    
    # Get user and resource
    user = User.query.get(user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")
    
    resource = get_resource(resource_id)
    if not resource:
        raise ValueError(f"Resource {resource_id} not found")
    
    # Validate booking request
    validate_booking_request(user, resource, start_dt, end_dt)
    
    # Check for conflicts
    if has_conflict(resource_id, start_dt, end_dt):
        raise ValueError("Booking conflicts with existing approved or pending booking")
    
    # Determine initial status based on approval workflow
    # Auto-approve if: resource is published AND not requires_approval
    # Otherwise: pending
    if resource.status == ResourceStatus.PUBLISHED and not resource.requires_approval:
        status = BookingStatus.APPROVED
    else:
        status = BookingStatus.PENDING
    
    booking = Booking(
        user_id=user_id,
        resource_id=resource_id,
        start_dt=start_dt,
        end_dt=end_dt,
        status=status
    )
    db.session.add(booking)
    db.session.commit()
    
    # Send notification
    try:
        from ..services.notify import send_notification
        if status == BookingStatus.APPROVED:
            send_notification([user_id], "Booking Approved", f"Your booking for {resource.title} has been automatically approved.")
        else:
            send_notification([user_id], "Booking Pending", f"Your booking for {resource.title} is pending approval.")
        send_notification([resource.created_by], "New Booking", f"A new booking has been created for {resource.title}.")
    except Exception:
        pass  # Notification failures shouldn't break booking creation
    
    return booking


def list_bookings_for_user(user_id):
    """
    List all bookings for a user.
    Automatically marks APPROVED bookings as COMPLETED if their end time has passed.
    
    Args:
        user_id: User ID
    
    Returns:
        Query object
    """
    now = datetime.utcnow()
    
    # Auto-complete any APPROVED bookings that have passed their end time
    approved_past_bookings = Booking.query.filter(
        Booking.user_id == user_id,
        Booking.status == BookingStatus.APPROVED,
        Booking.end_dt < now
    ).all()
    
    # Auto-complete these bookings
    for booking in approved_past_bookings:
        booking.status = BookingStatus.COMPLETED
        booking.updated_at = now
    
    if approved_past_bookings:
        db.session.commit()
    
    # Return all bookings for the user
    return Booking.query.filter_by(user_id=user_id).order_by(Booking.start_dt.desc())


def approve_booking(booking_id, approver_id):
    """
    Approve a booking with authorization and conflict recheck.
    
    Args:
        booking_id: Booking ID
        approver_id: User ID of approver
    
    Returns:
        Updated Booking instance
    
    Raises:
        ValueError: If booking not found, invalid status, unauthorized, or conflict exists
    """
    from ..models import User
    from ..models.user import UserRole
    
    booking = Booking.query.get(booking_id)
    if not booking:
        raise ValueError(f"Booking {booking_id} not found")
    
    # Check status is pending
    if booking.status != BookingStatus.PENDING:
        raise ValueError(f"Cannot approve booking with status {booking.status.value}")
    
    # Get approver and resource owner
    approver = User.query.get(approver_id)
    resource = get_resource(booking.resource_id)
    
    # Check authorization: staff/admin or resource owner
    if approver.role not in [UserRole.STAFF, UserRole.ADMIN] and resource.created_by != approver_id:
        raise ValueError("Only staff, admin, or resource owner can approve bookings")
    
    # Recheck conflicts right before approval
    if has_conflict(booking.resource_id, booking.start_dt, booking.end_dt, exclude_booking_id=booking_id):
        raise ValueError("Cannot approve: conflict detected with existing booking")
    
    booking.status = BookingStatus.APPROVED
    booking.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Send notification
    try:
        from ..services.notify import send_notification
        send_notification([booking.user_id], "Booking Approved", f"Your booking for {resource.title} has been approved.")
    except Exception:
        pass
    
    return booking


def reject_booking(booking_id, approver_id):
    """
    Reject a booking with authorization.
    
    Args:
        booking_id: Booking ID
        approver_id: User ID of approver
    
    Returns:
        Updated Booking instance
    
    Raises:
        ValueError: If booking not found, invalid status, or unauthorized
    """
    from ..models import User
    from ..models.user import UserRole
    
    booking = Booking.query.get(booking_id)
    if not booking:
        raise ValueError(f"Booking {booking_id} not found")
    
    # Check status is pending
    if booking.status != BookingStatus.PENDING:
        raise ValueError(f"Cannot reject booking with status {booking.status.value}")
    
    # Get approver and resource owner
    approver = User.query.get(approver_id)
    resource = get_resource(booking.resource_id)
    
    # Check authorization: staff/admin or resource owner
    if approver.role not in [UserRole.STAFF, UserRole.ADMIN] and resource.created_by != approver_id:
        raise ValueError("Only staff, admin, or resource owner can reject bookings")
    
    booking.status = BookingStatus.REJECTED
    booking.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Send notification
    try:
        from ..services.notify import send_notification
        send_notification([booking.user_id], "Booking Rejected", f"Your booking for {resource.title} has been rejected.")
    except Exception:
        pass
    
    return booking


def cancel_booking(booking_id, user_id):
    """
    Cancel a booking with authorization.
    
    Args:
        booking_id: Booking ID
        user_id: User ID requesting cancellation
    
    Returns:
        Updated Booking instance
    
    Raises:
        ValueError: If booking not found, invalid status, or unauthorized
    """
    from ..models import User
    from ..models.user import UserRole
    
    booking = Booking.query.get(booking_id)
    if not booking:
        raise ValueError(f"Booking {booking_id} not found")
    
    requester = User.query.get(user_id)
    
    # Check authorization: requester can cancel if pending/approved; staff/admin can cancel anytime
    can_cancel = False
    if booking.user_id == user_id and booking.status in [BookingStatus.PENDING, BookingStatus.APPROVED]:
        can_cancel = True
    elif requester.role in [UserRole.STAFF, UserRole.ADMIN]:
        can_cancel = True
    
    if not can_cancel:
        raise ValueError("You do not have permission to cancel this booking")
    
    booking.status = BookingStatus.CANCELLED
    booking.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Send notification
    try:
        from ..services.notify import send_notification
        resource = get_resource(booking.resource_id)
        send_notification([booking.user_id], "Booking Cancelled", f"Your booking for {resource.title} has been cancelled.")
    except Exception:
        pass
    
    return booking


def complete_booking(booking_id, admin_id):
    """
    Mark a booking as completed (admin only, only if past end_dt).
    
    Args:
        booking_id: Booking ID
        admin_id: User ID of admin
    
    Returns:
        Updated Booking instance
    
    Raises:
        ValueError: If booking not found, unauthorized, invalid status, or not past end_dt
    """
    from ..models import User
    from ..models.user import UserRole
    
    booking = Booking.query.get(booking_id)
    if not booking:
        raise ValueError(f"Booking {booking_id} not found")
    
    # Check authorization: admin only
    admin = User.query.get(admin_id)
    if admin.role != UserRole.ADMIN:
        raise ValueError("Only admin can complete bookings")
    
    # Check status is approved
    if booking.status != BookingStatus.APPROVED:
        raise ValueError(f"Cannot complete booking with status {booking.status.value}")
    
    # Check booking is past end_dt
    if datetime.utcnow() < booking.end_dt:
        raise ValueError("Cannot complete booking before end time")
    
    booking.status = BookingStatus.COMPLETED
    booking.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Send notification
    try:
        from ..services.notify import send_notification
        resource = get_resource(booking.resource_id)
        send_notification([booking.user_id], "Booking Completed", f"Your booking for {resource.title} has been marked as completed.")
    except Exception:
        pass
    
    return booking


def list_bookings_for_resource(resource_id):
    """
    List all bookings for a resource.
    
    Args:
        resource_id: Resource ID
    
    Returns:
        Query object ordered by start_dt desc
    """
    return Booking.query.filter_by(resource_id=resource_id).order_by(Booking.start_dt.desc())


# ============================================================================
# Message Operations
# ============================================================================

def get_booking(booking_id):
    """
    Get a booking by ID.
    
    Args:
        booking_id: Booking ID
    
    Returns:
        Booking instance or None
    """
    return Booking.query.get(booking_id)


def is_booking_participant(booking_id, user_id):
    """
    Check if a user is a participant in a booking (requester or resource owner).
    
    Args:
        booking_id: Booking ID
        user_id: User ID
    
    Returns:
        bool: True if user is a participant
    """
    from ..models import User
    from ..models.user import UserRole
    
    booking = get_booking(booking_id)
    if not booking:
        return False
    
    # Check if user is the requester
    if booking.user_id == user_id:
        return True
    
    # Check if user is the resource owner
    resource = get_resource(booking.resource_id)
    if resource and resource.created_by == user_id:
        return True
    
    # Check if user is admin (admins can always participate)
    user = get_user(user_id)
    if user and user.role == UserRole.ADMIN:
        return True
    
    return False


def get_message(message_id):
    """
    Get a message by ID.
    
    Args:
        message_id: Message ID
    
    Returns:
        Message instance or None
    """
    return Message.query.get(message_id)


def create_message(booking_id, sender_id, body, recipient_id=None):
    """
    Create a message for a booking with validation.
    
    Args:
        booking_id: Booking ID
        sender_id: User ID of sender
        body: Message body (will be sanitized)
        recipient_id: Optional - User ID of intended recipient (for directed messages)
    
    Returns:
        Message instance
    
    Raises:
        ValueError: If validation fails or user is not a participant
    """
    from ..services.sanitize import sanitize_body
    from ..models.booking import BookingStatus
    
    # Validate body
    if not body or not body.strip():
        raise ValueError("Message body cannot be empty")
    
    # Sanitize body
    body = sanitize_body(body)
    if not body:
        raise ValueError("Message body cannot be empty after sanitization")
    
    # Check if body exceeds max length (shouldn't happen after sanitize, but double-check)
    if len(body) > 2000:
        raise ValueError("Message body exceeds maximum length of 2000 characters")
    
    # Get booking
    booking = get_booking(booking_id)
    if not booking:
        raise ValueError(f"Booking {booking_id} not found")
    
    # Check booking status - don't allow messages on cancelled/rejected bookings
    if booking.status in [BookingStatus.CANCELLED, BookingStatus.REJECTED]:
        raise ValueError("Cannot send messages for cancelled or rejected bookings")
    
    # Check authorization
    if not is_booking_participant(booking_id, sender_id):
        raise ValueError("Only booking participants can send messages")
    
    # Validate recipient if provided
    if recipient_id:
        recipient = get_user(recipient_id)
        if not recipient:
            raise ValueError(f"Recipient user {recipient_id} not found")
        # Recipient must also be a participant
        if not is_booking_participant(booking_id, recipient_id):
            raise ValueError("Recipient must be a participant in this booking")
    
    message = Message(
        booking_id=booking_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        body=body
    )
    db.session.add(message)
    db.session.commit()
    return message


def list_messages(booking_id, page=1, per_page=20, include_hidden=False):
    """
    List messages for a booking with pagination.
    
    Args:
        booking_id: Booking ID
        page: Page number (1-indexed)
        per_page: Messages per page
        include_hidden: If True, include hidden messages (admin only)
    
    Returns:
        Pagination object with messages ordered by created_at ascending
    """
    query = Message.query.filter_by(booking_id=booking_id)
    
    # Exclude hidden messages unless admin requests them
    if not include_hidden:
        query = query.filter_by(is_hidden=False)
    
    query = query.order_by(Message.created_at.asc())
    
    # Use Flask-SQLAlchemy pagination
    return query.paginate(page=page, per_page=per_page, error_out=False)


def report_message(message_id, reporter_id):
    """
    Report a message (set is_reported flag).
    
    Args:
        message_id: Message ID
        reporter_id: User ID of reporter
    
    Returns:
        Updated Message instance
    
    Raises:
        ValueError: If message not found or user is not a participant
    """
    message = get_message(message_id)
    if not message:
        raise ValueError(f"Message {message_id} not found")
    
    # Check authorization - only participants can report
    if not is_booking_participant(message.booking_id, reporter_id):
        raise ValueError("Only booking participants can report messages")
    
    message.is_reported = True
    db.session.commit()
    return message


def hide_message(message_id, admin_id):
    """
    Hide a message (admin only).
    
    Args:
        message_id: Message ID
        admin_id: User ID of admin
    
    Returns:
        Updated Message instance
    
    Raises:
        ValueError: If message not found or user is not admin
    """
    from ..models.user import UserRole
    
    message = get_message(message_id)
    if not message:
        raise ValueError(f"Message {message_id} not found")
    
    # Check authorization - only admin can hide
    admin = get_user(admin_id)
    if not admin or admin.role != UserRole.ADMIN:
        raise ValueError("Only admins can hide messages")
    
    message.is_hidden = True
    db.session.commit()
    return message


# ============================================================================
# Review Operations
# ============================================================================

def user_has_completed_booking(user_id, resource_id):
    """
    Check if user has a completed booking for a resource.
    Automatically marks APPROVED bookings as COMPLETED if their end time has passed.
    
    Args:
        user_id: User ID
        resource_id: Resource ID
    
    Returns:
        bool: True if user has at least one completed booking for the resource
    """
    now = datetime.utcnow()
    
    # First, auto-complete any APPROVED bookings that have passed their end time
    approved_past_bookings = Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.user_id == user_id,
        Booking.status == BookingStatus.APPROVED,
        Booking.end_dt < now
    ).all()
    
    # Auto-complete these bookings
    for booking in approved_past_bookings:
        booking.status = BookingStatus.COMPLETED
        booking.updated_at = now
    
    if approved_past_bookings:
        db.session.commit()
    
    # Now check for completed bookings (including newly auto-completed ones)
    return Booking.query.filter(
        Booking.resource_id == resource_id,
        Booking.user_id == user_id,
        Booking.status == BookingStatus.COMPLETED
    ).first() is not None


def get_review(resource_id, user_id):
    """
    Get a review by resource_id and user_id.
    
    Args:
        resource_id: Resource ID
        user_id: User ID
    
    Returns:
        Review instance or None
    """
    return Review.query.filter_by(resource_id=resource_id, user_id=user_id).first()


def get_review_by_id(review_id):
    """
    Get a review by ID.
    
    Args:
        review_id: Review ID
    
    Returns:
        Review instance or None
    """
    return Review.query.get(review_id)


def _recompute_resource_rating(resource_id):
    """
    Recompute rating_avg and rating_count for a resource based on non-hidden reviews.
    
    Args:
        resource_id: Resource ID
    """
    from sqlalchemy import func
    
    # Aggregate only non-hidden reviews
    result = db.session.query(
        func.avg(Review.rating).label('avg'),
        func.count(Review.id).label('count')
    ).filter(
        Review.resource_id == resource_id,
        Review.is_hidden == False
    ).first()
    
    resource = get_resource(resource_id)
    if result and result.count > 0:
        resource.rating_avg = float(result.avg) if result.avg else 0.0
        resource.rating_count = int(result.count)
    else:
        resource.rating_avg = 0.0
        resource.rating_count = 0
    
    resource.updated_at = datetime.utcnow()
    db.session.commit()


def create_or_update_review(resource_id, user_id, rating, comment):
    """
    Create or update a review for a resource.
    
    Args:
        resource_id: Resource ID
        user_id: User ID
        rating: Rating (1-5)
        comment: Comment text
    
    Returns:
        Review instance
    
    Raises:
        ValueError: If validation fails or user is not eligible
    """
    from ..services.validators import validate_review_payload
    
    # Validate payload
    rating, comment = validate_review_payload(rating, comment)
    
    # Check eligibility
    if not user_has_completed_booking(user_id, resource_id):
        raise ValueError("User must have a completed booking to review this resource")
    
    # Check if review already exists
    existing = get_review(resource_id, user_id)
    if existing:
        # Update existing review
        existing.rating = rating
        existing.comment = comment
        existing.created_at = datetime.utcnow()  # Update timestamp on edit
        db.session.commit()
        # Recompute resource rating
        _recompute_resource_rating(resource_id)
        return existing
    
    # Create new review
    review = Review(
        resource_id=resource_id,
        user_id=user_id,
        rating=rating,
        comment=comment
    )
    db.session.add(review)
    db.session.commit()
    
    # Recompute resource rating
    _recompute_resource_rating(resource_id)
    
    return review


def list_reviews(resource_id, include_hidden=False, limit=20, offset=0):
    """
    List reviews for a resource.
    
    Args:
        resource_id: Resource ID
        include_hidden: If True, include hidden reviews (admin only)
        limit: Maximum number of reviews to return
        offset: Number of reviews to skip
    
    Returns:
        List of Review instances ordered by created_at desc
    """
    query = Review.query.filter_by(resource_id=resource_id)
    
    # Exclude hidden reviews unless admin requests them
    if not include_hidden:
        query = query.filter_by(is_hidden=False)
    
    return query.order_by(Review.created_at.desc()).limit(limit).offset(offset).all()


def hide_review(review_id, admin_id):
    """
    Hide a review (admin only).
    
    Args:
        review_id: Review ID
        admin_id: User ID of admin
    
    Returns:
        Updated Review instance
    
    Raises:
        ValueError: If review not found or user is not admin
    """
    from ..models.user import UserRole
    
    review = get_review_by_id(review_id)
    if not review:
        raise ValueError(f"Review {review_id} not found")
    
    # Check authorization - only admin can hide
    admin = get_user(admin_id)
    if not admin or admin.role != UserRole.ADMIN:
        raise ValueError("Only admins can hide reviews")
    
    review.is_hidden = True
    db.session.commit()
    
    # Recompute resource rating (hidden reviews excluded)
    _recompute_resource_rating(review.resource_id)
    
    return review


def unhide_review(review_id, admin_id):
    """
    Unhide a review (admin only).
    
    Args:
        review_id: Review ID
        admin_id: User ID of admin
    
    Returns:
        Updated Review instance
    
    Raises:
        ValueError: If review not found or user is not admin
    """
    from ..models.user import UserRole
    
    review = get_review_by_id(review_id)
    if not review:
        raise ValueError(f"Review {review_id} not found")
    
    # Check authorization - only admin can unhide
    admin = get_user(admin_id)
    if not admin or admin.role != UserRole.ADMIN:
        raise ValueError("Only admins can unhide reviews")
    
    review.is_hidden = False
    db.session.commit()
    
    # Recompute resource rating
    _recompute_resource_rating(review.resource_id)
    
    return review


def report_review(review_id):
    """
    Report a review for moderation.
    
    Args:
        review_id: Review ID
    
    Returns:
        Updated Review instance
    
    Raises:
        ValueError: If review not found
    """
    review = get_review_by_id(review_id)
    if not review:
        raise ValueError(f"Review {review_id} not found")
    
    review.is_reported = True
    db.session.commit()
    return review


def unreport_review(review_id):
    """
    Unreport a review (admin action).
    
    Args:
        review_id: Review ID
    
    Returns:
        Updated Review instance
    
    Raises:
        ValueError: If review not found
    """
    review = get_review_by_id(review_id)
    if not review:
        raise ValueError(f"Review {review_id} not found")
    
    review.is_reported = False
    db.session.commit()
    return review


def average_rating(resource_id):
    """
    Get average rating for a resource (from denormalized field).
    
    Args:
        resource_id: Resource ID
    
    Returns:
        float: Average rating (0.0 if no reviews)
    """
    resource = get_resource(resource_id)
    return resource.rating_avg if resource else 0.0


# ============================================================================
# Admin Operations
# ============================================================================

def list_pending_bookings(limit=50):
    """
    List pending bookings for admin review.
    
    Args:
        limit: Maximum number of bookings to return
    
    Returns:
        List of Booking instances with PENDING status
    """
    return Booking.query.filter_by(status=BookingStatus.PENDING).order_by(Booking.created_at.desc()).limit(limit).all()


def list_reported_messages(limit=50):
    """
    List reported messages for admin review.
    
    Args:
        limit: Maximum number of messages to return
    
    Returns:
        List of Message instances with is_reported=True
    """
    return Message.query.filter_by(is_reported=True).order_by(Message.created_at.desc()).limit(limit).all()


def list_reported_reviews(limit=50):
    """
    List reported reviews for admin review.
    
    Args:
        limit: Maximum number of reviews to return
    
    Returns:
        List of Review instances with is_reported=True
    """
    return Review.query.filter_by(is_reported=True).order_by(Review.created_at.desc()).limit(limit).all()


def list_hidden_reviews(limit=50):
    """
    List hidden reviews for admin review.
    
    Args:
        limit: Maximum number of reviews to return
    
    Returns:
        List of Review instances with is_hidden=True
    """
    return Review.query.filter_by(is_hidden=True).order_by(Review.created_at.desc()).limit(limit).all()


def list_users(role=None, limit=100):
    """
    List users with optional role filter.
    
    Args:
        role: UserRole enum to filter by (optional)
        limit: Maximum number of users to return
    
    Returns:
        List of User instances
    """
    query = User.query
    if role is not None:
        query = query.filter_by(role=role)
    return query.order_by(User.created_at.desc()).limit(limit).all()


def list_resources_admin(status=None, limit=100):
    """
    List resources with optional status filter (admin version, no default status filter).
    
    Args:
        status: ResourceStatus enum to filter by (optional)
        limit: Maximum number of resources to return
    
    Returns:
        List of Resource instances
    """
    query = Resource.query
    if status is not None:
        query = query.filter_by(status=status)
    return query.order_by(Resource.created_at.desc()).limit(limit).all()


def log_admin_action(admin_id, action, target_table, target_id, details="", ip_addr=None):
    """
    Log an admin action to the audit log.
    
    Args:
        admin_id: ID of admin performing the action
        action: Action name (e.g., "approve_booking", "hide_message")
        target_table: Table name (e.g., "bookings", "messages")
        target_id: ID of the target record
        details: Additional details (optional)
        ip_addr: IP address (optional)
    
    Returns:
        AdminLog instance
    """
    from ..models.admin_log import AdminLog
    
    log_entry = AdminLog(
        admin_id=admin_id,
        action=action,
        target_table=target_table,
        target_id=target_id,
        details=details,
        ip_addr=ip_addr
    )
    db.session.add(log_entry)
    db.session.commit()
    return log_entry


def list_admin_logs(limit=100):
    """
    List admin action logs.
    
    Args:
        limit: Maximum number of logs to return
    
    Returns:
        List of AdminLog instances ordered by created_at desc
    """
    from ..models.admin_log import AdminLog
    return AdminLog.query.order_by(AdminLog.created_at.desc()).limit(limit).all()


# ============================================================================
# Category Operations
# ============================================================================

def list_categories(include_inactive=False):
    """
    List all categories.
    
    Args:
        include_inactive: Include inactive categories (default: False)
    
    Returns:
        List of Category instances ordered by name
    """
    from ..models.category import Category
    query = Category.query
    if not include_inactive:
        query = query.filter_by(is_active=True)
    return query.order_by(Category.name).all()


def get_category(category_id):
    """
    Get a category by ID.
    
    Args:
        category_id: Category ID
    
    Returns:
        Category instance or None
    """
    from ..models.category import Category
    return Category.query.get(category_id)


def get_category_by_name(name):
    """
    Get a category by name.
    
    Args:
        name: Category name
    
    Returns:
        Category instance or None
    """
    from ..models.category import Category
    return Category.query.filter_by(name=name).first()


def create_category(name, description=None, is_active=True):
    """
    Create a new category.
    
    Args:
        name: Category name (unique)
        description: Optional description
        is_active: Active status (default: True)
    
    Returns:
        Category instance
    
    Raises:
        ValueError: If category name already exists
    """
    from ..models.category import Category
    
    # Check if category already exists
    existing = get_category_by_name(name)
    if existing:
        raise ValueError(f"Category '{name}' already exists")
    
    category = Category(
        name=name,
        description=description,
        is_active=is_active
    )
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category_id, data):
    """
    Update a category.
    
    Args:
        category_id: Category ID
        data: Dictionary with fields to update (name, description, is_active)
    
    Returns:
        Updated Category instance or None if not found
    
    Raises:
        ValueError: If new name conflicts with existing category
    """
    from ..models.category import Category
    
    category = get_category(category_id)
    if not category:
        return None
    
    # Check for name conflict if name is being changed
    if 'name' in data and data['name'] != category.name:
        existing = get_category_by_name(data['name'])
        if existing:
            raise ValueError(f"Category '{data['name']}' already exists")
        category.name = data['name']
    
    if 'description' in data:
        category.description = data['description']
    if 'is_active' in data:
        category.is_active = data['is_active']
    
    category.updated_at = datetime.utcnow()
    db.session.commit()
    return category


def deactivate_category(category_id):
    """
    Deactivate a category (soft delete).
    
    Args:
        category_id: Category ID
    
    Returns:
        Updated Category instance or None if not found
    """
    return update_category(category_id, {'is_active': False})


# ============================================================================
# Location Operations
# ============================================================================

def list_locations(include_inactive=False):
    """
    List all locations.
    
    Args:
        include_inactive: Include inactive locations (default: False)
    
    Returns:
        List of Location instances ordered by name
    """
    from ..models.location import Location
    query = Location.query
    if not include_inactive:
        query = query.filter_by(is_active=True)
    return query.order_by(Location.name).all()


def get_location(location_id):
    """
    Get a location by ID.
    
    Args:
        location_id: Location ID
    
    Returns:
        Location instance or None
    """
    from ..models.location import Location
    return Location.query.get(location_id)


def get_location_by_name(name):
    """
    Get a location by name.
    
    Args:
        name: Location name
    
    Returns:
        Location instance or None
    """
    from ..models.location import Location
    return Location.query.filter_by(name=name).first()


def create_location(name, building=None, floor=None, is_active=True):
    """
    Create a new location.
    
    Args:
        name: Location name (unique)
        building: Optional building name
        floor: Optional floor identifier
        is_active: Active status (default: True)
    
    Returns:
        Location instance
    
    Raises:
        ValueError: If location name already exists
    """
    from ..models.location import Location
    
    # Check if location already exists
    existing = get_location_by_name(name)
    if existing:
        raise ValueError(f"Location '{name}' already exists")
    
    location = Location(
        name=name,
        building=building,
        floor=floor,
        is_active=is_active
    )
    db.session.add(location)
    db.session.commit()
    return location


def update_location(location_id, data):
    """
    Update a location.
    
    Args:
        location_id: Location ID
        data: Dictionary with fields to update (name, building, floor, is_active)
    
    Returns:
        Updated Location instance or None if not found
    
    Raises:
        ValueError: If new name conflicts with existing location
    """
    from ..models.location import Location
    
    location = get_location(location_id)
    if not location:
        return None
    
    # Check for name conflict if name is being changed
    if 'name' in data and data['name'] != location.name:
        existing = get_location_by_name(data['name'])
        if existing:
            raise ValueError(f"Location '{data['name']}' already exists")
        location.name = data['name']
    
    if 'building' in data:
        location.building = data['building']
    if 'floor' in data:
        location.floor = data['floor']
    if 'is_active' in data:
        location.is_active = data['is_active']
    
    location.updated_at = datetime.utcnow()
    db.session.commit()
    return location


def deactivate_location(location_id):
    """
    Deactivate a location (soft delete).
    
    Args:
        location_id: Location ID
    
    Returns:
        Updated Location instance or None if not found
    """
    return update_location(location_id, {'is_active': False})

