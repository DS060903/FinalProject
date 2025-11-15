"""Booking endpoints.

IMPORTANT: Use DAL functions only. No direct DB queries.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from datetime import datetime

from ..data_access.dal import (
    create_booking, get_resource, approve_booking, reject_booking, cancel_booking,
    complete_booking, find_conflicts, list_bookings_for_user, get_booking
)
from ..models.user import UserRole
from ..models.booking import BookingStatus
from ..services.notify import send_notification

bookings_bp = Blueprint('bookings', __name__, url_prefix='/bookings')


@bookings_bp.route('', methods=['GET'])
@login_required
def list():
    """List all bookings for the current user."""
    bookings_list = list_bookings_for_user(current_user.id).all()
    
    return render_template('bookings/list.html', bookings=bookings_list)


def require_staff_or_admin():
    """Check if user is staff or admin."""
    if not current_user.is_authenticated:
        abort(401)
    if current_user.role not in [UserRole.STAFF, UserRole.ADMIN]:
        abort(403)


@bookings_bp.route('', methods=['POST'])
@login_required
def create():
    """Create a new booking."""
    # Rate limiting: 10 requests per minute per user/IP
    from ..services.rate_limit import allow
    rate_limit_key = f"{request.remote_addr}:{current_user.id}:booking_create"
    if not allow(rate_limit_key, 10, 60):
        flash("Too many requests. Please wait a minute and try again.", "warning")
        return redirect(url_for('resources.list_resources'))
    
    try:
        resource_id = int(request.form.get('resource_id'))
        start_str = request.form.get('start_dt')
        end_str = request.form.get('end_dt')
        
        # Parse datetime strings from HTML datetime-local input (YYYY-MM-DDTHH:MM)
        from ..services.validators import validate_time_window
        try:
            # Handle both 'T' separator and space separator
            start_str_clean = start_str.replace('T', ' ')
            end_str_clean = end_str.replace('T', ' ')
            
            # Parse format: YYYY-MM-DD HH:MM
            if len(start_str_clean) == 16:  # YYYY-MM-DD HH:MM
                start_dt = datetime.strptime(start_str_clean, '%Y-%m-%d %H:%M')
            else:
                start_dt = datetime.fromisoformat(start_str.replace('T', ' '))
            
            if len(end_str_clean) == 16:
                end_dt = datetime.strptime(end_str_clean, '%Y-%m-%d %H:%M')
            else:
                end_dt = datetime.fromisoformat(end_str.replace('T', ' '))
        except (ValueError, AttributeError) as e:
            flash(f"Invalid datetime format: {e}", 'error')
            return redirect(url_for('resources.detail', resource_id=resource_id))
        
        # Validate time window at controller layer (defense in depth)
        try:
            validate_time_window(start_dt, end_dt)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('resources.detail', resource_id=resource_id))
        
        booking = create_booking(
            user_id=current_user.id,
            resource_id=resource_id,
            start_dt=start_dt,
            end_dt=end_dt
        )
        
        # Flash message based on status
        if booking.status == BookingStatus.APPROVED:
            flash('Booking created and automatically approved!', 'success')
        else:
            flash('Booking created successfully. It is pending approval.', 'info')
        
        # Send notification stub (already done in DAL, but flash for user feedback)
        send_notification([current_user.id], "Booking Created", f"Booking #{booking.id} created with status: {booking.status.value}")
        
        return redirect(url_for('bookings.detail', booking_id=booking.id))
    except ValueError as e:
        flash(f'Error creating booking: {str(e)}', 'error')
        return redirect(request.referrer or url_for('resources.list_resources'))
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
        return redirect(request.referrer or url_for('resources.list_resources'))


@bookings_bp.route('/<int:booking_id>', methods=['GET'])
@login_required
def detail(booking_id):
    """Get booking detail."""
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    # Check access: booking owner, resource creator, or admin
    if booking.user_id != current_user.id:
        resource = get_resource(booking.resource_id)
        if resource.created_by != current_user.id and current_user.role != UserRole.ADMIN:
            abort(403)
    
    # Check for conflicts (for display)
    conflicts = find_conflicts(booking.resource_id, booking.start_dt, booking.end_dt, exclude_booking_id=booking.id)
    has_conflict_warning = len(conflicts) > 0
    
    resource = get_resource(booking.resource_id)
    
    # Fetch recent messages for approval context (last 3 messages)
    from ..data_access.dal import list_messages as dal_list_messages
    recent_messages_pagination = dal_list_messages(booking_id, page=1, per_page=3, include_hidden=False)
    recent_messages = recent_messages_pagination.items if recent_messages_pagination else []
    message_count = recent_messages_pagination.total if recent_messages_pagination else 0
    
    return render_template('bookings/detail.html', 
                         booking=booking, 
                         resource=resource,
                         has_conflict_warning=has_conflict_warning,
                         conflicts=conflicts,
                         recent_messages=recent_messages,
                         message_count=message_count)


@bookings_bp.route('/<int:booking_id>/approve', methods=['POST'])
@login_required
def approve(booking_id):
    """Approve a booking (admin only)."""
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    resource = get_resource(booking.resource_id)
    
    # Check authorization: admin only
    if current_user.role != UserRole.ADMIN:
        flash('Only administrators can approve bookings.', 'error')
        abort(403)
    
    try:
        approve_booking(booking_id, current_user.id)
        flash('Booking approved successfully.', 'success')
        send_notification([booking.user_id], "Booking Approved", f"Your booking for {resource.title} has been approved.")
    except ValueError as e:
        flash(f'Error approving booking: {str(e)}', 'error')
    
    return redirect(url_for('bookings.detail', booking_id=booking_id))


@bookings_bp.route('/<int:booking_id>/reject', methods=['POST'])
@login_required
def reject(booking_id):
    """Reject a booking (admin only)."""
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    resource = get_resource(booking.resource_id)
    
    # Check authorization: admin only
    if current_user.role != UserRole.ADMIN:
        flash('Only administrators can reject bookings.', 'error')
        abort(403)
    
    try:
        reject_booking(booking_id, current_user.id)
        flash('Booking rejected.', 'success')
        send_notification([booking.user_id], "Booking Rejected", f"Your booking for {resource.title} has been rejected.")
    except ValueError as e:
        flash(f'Error rejecting booking: {str(e)}', 'error')
    
    return redirect(url_for('bookings.detail', booking_id=booking_id))


@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel(booking_id):
    """Cancel a booking (owner or admin)."""
    booking = get_booking(booking_id)
    if not booking:
        abort(404)
    
    # Check access: owner or admin
    if booking.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        abort(403)
    
    try:
        cancel_booking(booking_id, current_user.id)
        flash('Booking cancelled.', 'success')
        resource = get_resource(booking.resource_id)
        send_notification([booking.user_id], "Booking Cancelled", f"Your booking for {resource.title} has been cancelled.")
    except ValueError as e:
        flash(f'Error cancelling booking: {str(e)}', 'error')
    
    return redirect(url_for('bookings.detail', booking_id=booking_id))


@bookings_bp.route('/<int:booking_id>/complete', methods=['POST'])
@login_required
def complete(booking_id):
    """Complete a booking (admin only)."""
    if current_user.role != UserRole.ADMIN:
        abort(403)
    
    try:
        complete_booking(booking_id, current_user.id)
        flash('Booking marked as completed.', 'success')
        booking = get_booking(booking_id)
        resource = get_resource(booking.resource_id)
        send_notification([booking.user_id], "Booking Completed", f"Your booking for {resource.title} has been marked as completed.")
    except ValueError as e:
        flash(f'Error completing booking: {str(e)}', 'error')
    
    return redirect(url_for('bookings.detail', booking_id=booking_id))

