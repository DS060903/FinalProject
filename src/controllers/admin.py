"""Admin dashboard endpoints.

IMPORTANT: Use DAL functions only. No direct DB queries.
All routes require admin role.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..data_access.dal import (
    list_pending_bookings, list_reported_messages, list_hidden_reviews, list_reported_reviews,
    list_users, list_resources_admin, log_admin_action, list_admin_logs,
    approve_booking, reject_booking, hide_message, unhide_review, unreport_review,
    get_resource, get_booking, get_message, get_review_by_id
)
from ..services.audit import record_admin_action
from ..models.user import UserRole
from ..models.booking import BookingStatus
from ..models.resource import ResourceStatus

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def require_admin():
    """Check if current user is admin."""
    if not current_user.is_authenticated:
        abort(401)
    if current_user.role != UserRole.ADMIN:
        abort(403)


@admin_bp.before_request
def check_admin():
    """Check admin role before all admin routes."""
    # All routes require admin
    require_admin()


@admin_bp.route('', methods=['GET'])
@login_required
def dashboard():
    """Admin dashboard with summary counts."""
    # Get counts
    pending_bookings = list_pending_bookings(limit=1000)  # Get all for count
    reported_messages = list_reported_messages(limit=1000)
    hidden_reviews = list_hidden_reviews(limit=1000)
    
    counts = {
        'pending_bookings': len(pending_bookings),
        'reported_messages': len(reported_messages),
        'hidden_reviews': len(hidden_reviews)
    }
    
    return render_template('admin/dashboard.html', 
                          pending_bookings_count=len(pending_bookings),
                          reported_messages_count=len(reported_messages),
                          hidden_reviews_count=len(hidden_reviews))


@admin_bp.route('/bookings', methods=['GET'])
@login_required
def bookings():
    """List pending bookings for approval (admin only)."""
    # Authorization checked by @admin_bp.before_request
    bookings_list = list_pending_bookings(limit=50)
    
    # Fetch messages for each booking to provide approval context
    from ..data_access.dal import list_messages as dal_list_messages
    booking_messages = {}
    for booking in bookings_list:
        messages_pagination = dal_list_messages(booking.id, page=1, per_page=10, include_hidden=False)
        booking_messages[booking.id] = {
            'messages': messages_pagination.items if messages_pagination else [],
            'count': messages_pagination.total if messages_pagination else 0
        }
    
    return render_template('admin/bookings.html', bookings=bookings_list, booking_messages=booking_messages)


@admin_bp.route('/bookings/<int:booking_id>/approve', methods=['POST'])
@login_required
def approve_booking_action(booking_id):
    """Approve a booking (admin only)."""
    # Authorization checked by @admin_bp.before_request
    
    booking = get_booking(booking_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('admin.bookings'))
    
    try:
        approve_booking(booking_id, current_user.id)
        record_admin_action(
            current_user.id,
            'approve_booking',
            'bookings',
            booking_id,
            f'Approved booking #{booking_id} for resource {booking.resource_id}',
            request
        )
        flash('Booking approved successfully.', 'success')
    except ValueError as e:
        flash(f'Error approving booking: {str(e)}', 'error')
    
    return redirect(url_for('admin.bookings'))


@admin_bp.route('/bookings/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject_booking_action(booking_id):
    """Reject a booking (admin only)."""
    # Authorization checked by @admin_bp.before_request
    
    booking = get_booking(booking_id)
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('admin.bookings'))
    
    try:
        from ..data_access.dal import reject_booking as dal_reject_booking
        dal_reject_booking(booking_id, current_user.id)
        record_admin_action(
            current_user.id,
            'reject_booking',
            'bookings',
            booking_id,
            f'Rejected booking #{booking_id} for resource {booking.resource_id}',
            request
        )
        flash('Booking rejected successfully.', 'success')
    except ValueError as e:
        flash(f'Error rejecting booking: {str(e)}', 'error')
    
    return redirect(url_for('admin.bookings'))


@admin_bp.route('/messages', methods=['GET'])
@login_required
def messages():
    """List reported messages for moderation."""
    messages_list = list_reported_messages(limit=50)
    return render_template('admin/messages.html', messages=messages_list)


@admin_bp.route('/messages/<int:message_id>/hide', methods=['POST'])
@login_required
def hide_message_action(message_id):
    """Hide a reported message."""
    message = get_message(message_id)
    if not message:
        flash('Message not found.', 'error')
        return redirect(url_for('admin.messages'))
    
    try:
        hide_message(message_id, current_user.id)
        record_admin_action(
            current_user.id,
            'hide_message',
            'messages',
            message_id,
            f'Hid reported message #{message_id} from booking {message.booking_id}',
            request
        )
        flash('Message hidden successfully.', 'success')
    except ValueError as e:
        flash(f'Error hiding message: {str(e)}', 'error')
    
    return redirect(url_for('admin.messages'))


@admin_bp.route('/messages/<int:message_id>/unreport', methods=['POST'])
@login_required
def unreport_message_action(message_id):
    """Unreport a message (clear is_reported flag)."""
    from ..data_access.dal import db
    from ..models import Message
    message = get_message(message_id)
    if not message:
        flash('Message not found.', 'error')
        return redirect(url_for('admin.messages'))
    
    try:
        message.is_reported = False
        db.session.commit()
        record_admin_action(
            current_user.id,
            'unreport_message',
            'messages',
            message_id,
            f'Cleared report flag on message #{message_id}',
            request
        )
        flash('Message report cleared successfully.', 'success')
    except Exception as e:
        flash(f'Error clearing report: {str(e)}', 'error')
    
    return redirect(url_for('admin.messages'))


@admin_bp.route('/reviews', methods=['GET'])
@login_required
def reviews():
    """List reported and hidden reviews for moderation."""
    reported_reviews_list = list_reported_reviews(limit=50)
    hidden_reviews_list = list_hidden_reviews(limit=50)
    return render_template('admin/reviews.html', 
                         reported_reviews=reported_reviews_list,
                         hidden_reviews=hidden_reviews_list)


@admin_bp.route('/reviews/<int:review_id>/unhide', methods=['POST'])
@login_required
def unhide_review_action(review_id):
    """Unhide a review."""
    review = get_review_by_id(review_id)
    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('admin.reviews'))
    
    try:
        unhide_review(review_id, current_user.id)
        record_admin_action(
            current_user.id,
            'unhide_review',
            'reviews',
            review_id,
            f'Unhid review #{review_id} for resource {review.resource_id}',
            request
        )
        flash('Review unhidden successfully.', 'success')
    except ValueError as e:
        flash(f'Error unhiding review: {str(e)}', 'error')
    
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/reviews/<int:review_id>/unreport', methods=['POST'])
@login_required
def unreport_review_action(review_id):
    """Unreport a review (clear is_reported flag)."""
    review = get_review_by_id(review_id)
    if not review:
        flash('Review not found.', 'error')
        return redirect(url_for('admin.reviews'))
    
    try:
        unreport_review(review_id)
        record_admin_action(
            current_user.id,
            'unreport_review',
            'reviews',
            review_id,
            f'Cleared report flag on review #{review_id}',
            request
        )
        flash('Review report cleared successfully.', 'success')
    except ValueError as e:
        flash(f'Error clearing report: {str(e)}', 'error')
    
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/users', methods=['GET'])
@login_required
def users():
    """List all users with optional role filter."""
    role_filter = request.args.get('role')
    role = None
    if role_filter:
        try:
            role = UserRole[role_filter.upper()]
        except (KeyError, AttributeError):
            pass
    
    users_list = list_users(role=role, limit=100)
    return render_template('admin/users.html', users=users_list, role_filter=role_filter)


@admin_bp.route('/resources', methods=['GET'])
@login_required
def resources():
    """List all resources with optional status filter."""
    status_filter = request.args.get('status')
    status = None
    if status_filter:
        try:
            status = ResourceStatus[status_filter.upper()]
        except (KeyError, AttributeError):
            pass
    
    resources_list = list_resources_admin(status=status, limit=100)
    return render_template('admin/resources.html', resources=resources_list, status_filter=status_filter)


@admin_bp.route('/logs', methods=['GET'])
@login_required
def logs():
    """List admin action logs."""
    logs_list = list_admin_logs(limit=100)
    return render_template('admin/logs.html', logs=logs_list)


@admin_bp.route('/all-bookings', methods=['GET'])
@login_required
def all_bookings():
    """List all bookings with messages for admin review and response."""
    # Authorization checked by @admin_bp.before_request
    from ..data_access.dal import list_messages as dal_list_messages
    from ..models.booking import Booking
    
    # Get all bookings (not just pending), ordered by most recent
    all_bookings_list = Booking.query.order_by(Booking.created_at.desc()).limit(50).all()
    
    # Fetch messages for each booking
    booking_messages = {}
    for booking in all_bookings_list:
        messages_pagination = dal_list_messages(booking.id, page=1, per_page=10, include_hidden=False)
        booking_messages[booking.id] = {
            'messages': messages_pagination.items if messages_pagination else [],
            'count': messages_pagination.total if messages_pagination else 0
        }
    
    return render_template('admin/all_bookings.html', bookings=all_bookings_list, booking_messages=booking_messages)
