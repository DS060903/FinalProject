"""Review endpoints.

IMPORTANT: Use DAL functions only. No direct DB queries.
"""
from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from ..data_access.dal import (
    create_or_update_review, get_resource, user_has_completed_booking,
    get_review, hide_review, unhide_review, get_review_by_id, report_review, unreport_review
)
from ..services.validators import validate_review_payload
from ..models.user import UserRole

reviews_bp = Blueprint('reviews', __name__, url_prefix='/resources/<int:resource_id>/reviews')


@reviews_bp.route('', methods=['POST'])
@login_required
def create(resource_id):
    """Create or update a review for a resource."""
    resource = get_resource(resource_id)
    if not resource:
        abort(404)
    
    try:
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment', '').strip()
        
        # Validate payload
        rating, comment = validate_review_payload(rating, comment)
        
        # Check eligibility
        if not user_has_completed_booking(current_user.id, resource_id):
            flash('You must have a completed booking for this resource to leave a review.', 'error')
            return redirect(url_for('resources.detail', resource_id=resource_id))
        
        # Create or update review
        create_or_update_review(resource_id, current_user.id, rating, comment)
        flash('Review submitted successfully.', 'success')
    except ValueError as e:
        flash(f'Error creating review: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


# Admin routes for moderation
@reviews_bp.route('/<int:review_id>/hide', methods=['POST'])
@login_required
def hide(resource_id, review_id):
    """Hide a review (admin only)."""
    if current_user.role != UserRole.ADMIN:
        abort(403)
    
    try:
        review = hide_review(review_id, current_user.id)
        flash('Review hidden successfully.', 'success')
    except ValueError as e:
        flash(f'Error hiding review: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


@reviews_bp.route('/<int:review_id>/unhide', methods=['POST'])
@login_required
def unhide(resource_id, review_id):
    """Unhide a review (admin only)."""
    if current_user.role != UserRole.ADMIN:
        abort(403)
    
    try:
        review = unhide_review(review_id, current_user.id)
        flash('Review unhidden successfully.', 'success')
    except ValueError as e:
        flash(f'Error unhiding review: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


@reviews_bp.route('/<int:review_id>/report', methods=['POST'])
@login_required
def report(resource_id, review_id):
    """Report a review for moderation."""
    try:
        review = report_review(review_id)
        flash('Review reported successfully. An admin will review it.', 'success')
    except ValueError as e:
        flash(f'Error reporting review: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


@reviews_bp.route('/<int:review_id>/unreport', methods=['POST'])
@login_required
def unreport(resource_id, review_id):
    """Unreport a review (admin only)."""
    if current_user.role != UserRole.ADMIN:
        abort(403)
    
    try:
        review = unreport_review(review_id)
        flash('Review unreported successfully.', 'success')
    except ValueError as e:
        flash(f'Error unreporting review: {str(e)}', 'error')
    
    # Redirect back to admin reviews page
    return redirect(url_for('admin.reviews'))

