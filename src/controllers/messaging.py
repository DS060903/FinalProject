"""Messaging endpoints.

IMPORTANT: Use DAL functions only. No direct DB queries.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..models.user import db
from ..data_access.dal import (
    get_booking,
    is_booking_participant,
    create_message as dal_create_message,
    list_messages as dal_list_messages,
    report_message,
    hide_message,
    get_resource,
    get_user
)
from ..models.user import UserRole
from ..services.antiabuse import check_cooldown

messaging_bp = Blueprint('messaging', __name__, url_prefix='/bookings/<int:booking_id>/messages')

# Separate blueprint for messages list (no booking_id in URL)
messages_list_bp = Blueprint('messages_list', __name__, url_prefix='/messages')


@messages_list_bp.route('/my-messages', methods=['GET'])
@login_required
def my_messages():
    """List all bookings with messages for the current user."""
    from ..models.booking import Booking
    from ..models.resource import Resource
    from ..models.message import Message
    from ..models.user import UserRole
    from sqlalchemy import or_
    
    # Get all bookings where the user is a participant:
    # 1. Bookings they created (user_id = current_user.id)
    # 2. Bookings for resources they own (resource.created_by = current_user.id)
    # 3. If admin, they can see any booking where they've sent a message
    
    if current_user.role == UserRole.ADMIN:
        # Admins can see any booking where they've participated in messages
        booking_ids_with_admin_messages = db.session.query(Message.booking_id).filter(
            Message.sender_id == current_user.id
        ).distinct().all()
        booking_ids = [bid[0] for bid in booking_ids_with_admin_messages]
        
        # Also include bookings they created or own resources for
        bookings_query = Booking.query.outerjoin(Resource).filter(
            or_(
                Booking.user_id == current_user.id,
                Resource.created_by == current_user.id,
                Booking.id.in_(booking_ids) if booking_ids else False
            )
        )
    else:
        # Non-admins: show bookings they created OR resources they own
        bookings_query = Booking.query.outerjoin(Resource).filter(
            or_(
                Booking.user_id == current_user.id,
                Resource.created_by == current_user.id
            )
        )
    
    bookings = bookings_query.order_by(Booking.created_at.desc()).all()
    
    # Filter to only bookings that have messages
    bookings_with_messages = []
    for booking in bookings:
        messages = dal_list_messages(booking.id, page=1, per_page=1, include_hidden=False)
        if messages.total > 0:
            bookings_with_messages.append({
                'booking': booking,
                'message_count': messages.total,
                'last_message': messages.items[0] if messages.items else None
            })
    
    return render_template('messaging/my_messages.html', bookings_with_messages=bookings_with_messages)


def can_access_booking(booking_id, user_id):
    """Check if user can access this booking (participant or admin)."""
    from ..models.user import UserRole
    
    if is_booking_participant(booking_id, user_id):
        return True
    
    # Admins can always access
    user = get_user(user_id)
    if user and user.role == UserRole.ADMIN:
        return True
    
    return False


@messaging_bp.route('', methods=['GET'])
@login_required
def list_messages(booking_id):
    """List messages for a booking with pagination."""
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    # Check authorization
    if not can_access_booking(booking_id, current_user.id):
        abort(403)
    
    # Get pagination parameters with validation
    from ..services.validators import validate_pagination
    page = validate_pagination(request.args.get('page'), default=1, minv=1, maxv=1000)
    per_page = validate_pagination(request.args.get('per_page'), default=20, minv=1, maxv=100)
    
    # Include hidden messages only for admins
    include_hidden = current_user.role == UserRole.ADMIN
    
    # Get paginated messages
    pagination = dal_list_messages(booking_id, page=page, per_page=per_page, include_hidden=include_hidden)
    
    # Get resource for display
    resource = get_resource(booking.resource_id)
    
    return render_template(
        'messaging/thread.html',
        booking=booking,
        resource=resource,
        messages=pagination.items,
        pagination=pagination
    )


@messaging_bp.route('', methods=['POST'])
@login_required
def create_message(booking_id):
    """Send a message for a booking."""
    # Rate limiting: 10 requests per minute per user/IP
    from ..services.rate_limit import allow
    rate_limit_key = f"{request.remote_addr}:{current_user.id}:message_create"
    if not allow(rate_limit_key, 10, 60):
        flash("Too many requests. Please wait a minute and try again.", "warning")
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('messaging.list_messages', booking_id=booking_id, page=page))
    
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    # Check authorization
    if not can_access_booking(booking_id, current_user.id):
        abort(403)
    
    body = request.form.get('body', '').strip()
    recipient_str = request.form.get('recipient_id', '')  # Can be user_id or "admin"
    
    # Parse recipient
    recipient_id = None
    if recipient_str:
        if recipient_str == 'admin':
            # Find an admin user
            from ..models.user import UserRole
            from ..models import User
            admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
            if admin_user:
                recipient_id = admin_user.id
        else:
            try:
                recipient_id = int(recipient_str)
            except (ValueError, TypeError):
                pass
    
    try:
        # Check cooldown
        check_cooldown(current_user.id, booking_id, seconds=10)
        
        # Create message (includes sanitization and validation)
        dal_create_message(booking_id, current_user.id, body, recipient_id=recipient_id)
        flash('Message sent successfully.', 'success')
    except ValueError as e:
        flash(f'Error sending message: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    # Redirect to same page with current pagination
    from ..services.validators import validate_pagination
    page = validate_pagination(request.args.get('page'), default=1, minv=1, maxv=1000)
    return redirect(url_for('messaging.list_messages', booking_id=booking_id, page=page))


@messaging_bp.route('/<int:message_id>/report', methods=['POST'])
@login_required
def report_message_view(booking_id, message_id):
    """Report a message."""
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    # Check authorization
    if not can_access_booking(booking_id, current_user.id):
        abort(403)
    
    try:
        report_message(message_id, current_user.id)
        flash('Message reported. Thank you for your feedback.', 'info')
    except ValueError as e:
        flash(f'Error reporting message: {str(e)}', 'error')
    
    from ..services.validators import validate_pagination
    page = validate_pagination(request.args.get('page'), default=1, minv=1, maxv=1000)
    return redirect(url_for('messaging.list_messages', booking_id=booking_id, page=page))


# Admin-only route for hiding messages
@messaging_bp.route('/<int:message_id>/hide', methods=['POST'])
@login_required
def hide_message_view(booking_id, message_id):
    """Hide a message (admin only)."""
    if current_user.role != UserRole.ADMIN:
        abort(403)
    
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    try:
        hide_message(message_id, current_user.id)
        flash('Message hidden successfully.', 'success')
    except ValueError as e:
        flash(f'Error hiding message: {str(e)}', 'error')
    
    from ..services.validators import validate_pagination
    page = validate_pagination(request.args.get('page'), default=1, minv=1, maxv=1000)
    return redirect(url_for('messaging.list_messages', booking_id=booking_id, page=page))

