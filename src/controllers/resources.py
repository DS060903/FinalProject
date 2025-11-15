"""Resource endpoints.

IMPORTANT: Use DAL functions only. No direct DB queries.
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, abort, current_app
from flask_login import login_required, current_user

from ..data_access.dal import (
    create_resource, list_resources as dal_list_resources, get_resource, update_resource, archive_resource, unarchive_resource,
    add_resource_images, remove_resource_image, average_rating,
    list_reviews, user_has_completed_booking, get_review,
    list_categories, list_locations, get_category_by_name, get_location_by_name
)
from ..models.resource import ResourceStatus
from ..models.user import UserRole

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')


def require_staff_or_admin():
    """Check if user is staff or admin."""
    if not current_user.is_authenticated:
        abort(401)
    if current_user.role not in [UserRole.STAFF, UserRole.ADMIN]:
        abort(403)


def require_owner_or_admin(resource):
    """Check if user is the resource owner, staff, or admin.
    
    Staff and admins can manage any resource.
    """
    if not current_user.is_authenticated:
        abort(401)
    
    is_owner = resource.created_by == current_user.id
    is_staff = current_user.role == UserRole.STAFF
    is_admin = current_user.role == UserRole.ADMIN
    
    if not (is_owner or is_staff or is_admin):
        flash('You must be staff or admin to manage resources.', 'error')
        abort(403)


@resources_bp.route('', methods=['GET'])
def list_resources():
    """List resources with simple keyword search."""
    filters = {}
    
    # Simple keyword search (query string directly added to filters)
    user_query = request.args.get('query', '')
    if user_query:
        filters['query'] = user_query
    
    # Parse query parameters for traditional filters
    if request.args.get('category'):
        category = request.args.get('category')
        # Validate against database
        if get_category_by_name(category):
            filters['category'] = category
        else:
            flash(f'Invalid category: {category}. Please select from the dropdown.', 'warning')
    
    if request.args.get('location'):
        location = request.args.get('location')
        # Validate against database
        if get_location_by_name(location):
            filters['location'] = location
        else:
            flash(f'Invalid location: {location}. Please select from the dropdown.', 'warning')
    if request.args.get('capacity_min'):
        try:
            filters['capacity_min'] = int(request.args.get('capacity_min'))
        except ValueError:
            pass
    if request.args.get('date'):
        filters['date'] = request.args.get('date')
    if request.args.get('status'):
        try:
            filters['status'] = ResourceStatus[request.args.get('status').upper()]
        except (KeyError, AttributeError):
            pass
    if request.args.get('sort'):
        filters['sort'] = request.args.get('sort')
    
    resources = dal_list_resources(filters).all()
    
    # Fetch categories and locations for dropdowns
    categories = list_categories()
    locations = list_locations()
    
    return render_template('resources/list.html', 
                         resources=resources, 
                         filters=filters,
                         query=user_query,
                         categories=categories,
                         locations=locations)


@resources_bp.route('/<int:resource_id>', methods=['GET'])
def detail(resource_id):
    """Get resource detail."""
    resource = get_resource(resource_id)
    if not resource:
        abort(404)
    
    # Get rating info from denormalized fields
    rating_avg = resource.rating_avg
    rating_count = resource.rating_count
    
    # Get reviews (non-hidden, recent 20)
    reviews = list_reviews(resource_id, include_hidden=False, limit=20, offset=0)
    
    # Check if current user can review (has completed booking and no existing review)
    can_review = False
    user_review = None
    if current_user.is_authenticated:
        has_completed = user_has_completed_booking(current_user.id, resource_id)
        if has_completed:
            user_review = get_review(resource_id, current_user.id)
            can_review = True  # Can review (or update existing)
    
    return render_template(
        'resources/detail.html',
        resource=resource,
        rating_avg=rating_avg,
        rating_count=rating_count,
        reviews=reviews,
        can_review=can_review,
        user_review=user_review
    )


@resources_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new resource (staff/admin only)."""
    require_staff_or_admin()
    
    if request.method == 'POST':
        # Rate limiting: 10 requests per minute per user/IP
        from ..services.rate_limit import allow
        rate_limit_key = f"{request.remote_addr}:{current_user.id}:resource_create"
        if not allow(rate_limit_key, 10, 60):
            flash("Too many requests. Please wait a minute and try again.", "warning")
            return redirect(url_for('resources.list_resources'))
        try:
            # Validate category and location against database
            category = request.form.get('category', '').strip() or None
            location = request.form.get('location', '').strip() or None
            
            if category and not get_category_by_name(category):
                categories = list_categories()
                locations = list_locations()
                flash(f'Invalid category selected. Please choose from the dropdown options.', 'error')
                return render_template('resources/create.html', categories=categories, locations=locations)
            
            if location and not get_location_by_name(location):
                categories = list_categories()
                locations = list_locations()
                flash(f'Invalid location selected. Please choose from the dropdown options.', 'error')
                return render_template('resources/create.html', categories=categories, locations=locations)
            
            data = {
                'title': request.form.get('title', '').strip(),
                'description': request.form.get('description', '').strip(),
                'category': category,
                'location': location,
                'capacity': int(request.form.get('capacity', 0)),
                'status': ResourceStatus[request.form.get('status', 'draft').upper()],
                'requires_approval': request.form.get('requires_approval') == 'on',
                'created_by': current_user.id
            }
            
            resource = create_resource(data)
            
            # Handle image upload if provided (exact same logic as upload_images route)
            if 'images' in request.files:
                files = request.files.getlist('images')
                # Check if any files were actually selected (have filenames)
                if files and any(f.filename for f in files):
                    try:
                        stored_paths = add_resource_images(resource.id, files)
                        flash(f'Resource created successfully with {len(stored_paths)} image(s).', 'success')
                    except ValueError as e:
                        flash(f'Resource created successfully, but image upload failed: {str(e)}', 'warning')
                    except Exception as e:
                        import traceback
                        current_app.logger.error(f"Image upload error: {str(e)}\n{traceback.format_exc()}")
                        flash(f'Resource created successfully, but image upload failed: {str(e)}', 'warning')
                else:
                    flash('Resource created successfully.', 'success')
            else:
                flash('Resource created successfully.', 'success')
            
            return redirect(url_for('resources.detail', resource_id=resource.id))
        except (ValueError, KeyError) as e:
            flash(f'Error creating resource: {str(e)}', 'error')
            categories = list_categories()
            locations = list_locations()
            return render_template('resources/create.html', categories=categories, locations=locations)
    
    # GET request: render create form with dropdowns
    categories = list_categories()
    locations = list_locations()
    return render_template('resources/create.html', categories=categories, locations=locations)


@resources_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(resource_id):
    """Edit a resource (owner or admin only)."""
    resource = get_resource(resource_id)
    if not resource:
        abort(404)
    
    # Check authorization: must be resource owner or admin
    require_owner_or_admin(resource)
    
    if request.method == 'GET':
        categories = list_categories()
        locations = list_locations()
        return render_template('resources/edit.html', resource=resource, categories=categories, locations=locations)
    
    # POST: Update resource
    # Rate limiting: 10 requests per minute per user/IP
    from ..services.rate_limit import allow
    rate_limit_key = f"{request.remote_addr}:{current_user.id}:resource_edit"
    if not allow(rate_limit_key, 10, 60):
        flash("Too many requests. Please wait a minute and try again.", "warning")
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    try:
        # Validate category and location against database
        category = request.form.get('category', '').strip() or None
        location = request.form.get('location', '').strip() or None
        
        if category and not get_category_by_name(category):
            categories = list_categories()
            locations = list_locations()
            flash(f'Invalid category selected. Please choose from the dropdown options.', 'error')
            return render_template('resources/edit.html', resource=resource, categories=categories, locations=locations)
        
        if location and not get_location_by_name(location):
            categories = list_categories()
            locations = list_locations()
            flash(f'Invalid location selected. Please choose from the dropdown options.', 'error')
            return render_template('resources/edit.html', resource=resource, categories=categories, locations=locations)
        
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'category': category,
            'location': location,
            'capacity': int(request.form.get('capacity', 0)),
            'status': ResourceStatus[request.form.get('status', 'draft').upper()],
            'requires_approval': request.form.get('requires_approval') == 'on'
        }
        
        update_resource(resource_id, data)
        flash('Resource updated successfully.', 'success')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    except (ValueError, KeyError) as e:
        flash(f'Error updating resource: {str(e)}', 'error')
        return render_template('resources/edit.html', resource=resource)


@resources_bp.route('/<int:resource_id>/archive', methods=['POST'])
@login_required
def archive(resource_id):
    """Archive a resource (owner or admin only)."""
    resource = get_resource(resource_id)
    if not resource:
        abort(404)
    
    # Check authorization: must be resource owner or admin
    require_owner_or_admin(resource)
    
    try:
        archive_resource(resource_id)
        flash('Resource archived successfully.', 'success')
    except ValueError as e:
        flash(f'Error archiving resource: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


@resources_bp.route('/<int:resource_id>/unarchive', methods=['POST'])
@login_required
def unarchive(resource_id):
    """Unarchive a resource (owner or admin only)."""
    resource = get_resource(resource_id)
    if not resource:
        abort(404)
    
    # Check authorization: must be resource owner or admin
    require_owner_or_admin(resource)
    
    try:
        unarchive_resource(resource_id)
        flash('Resource unarchived successfully.', 'success')
    except ValueError as e:
        flash(f'Error unarchiving resource: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


@resources_bp.route('/<int:resource_id>/images', methods=['POST'])
@login_required
def upload_images(resource_id):
    """Upload images to a resource (staff/admin or resource owner only)."""
    resource = get_resource(resource_id)
    if not resource:
        abort(404)
    
    # Check permissions: staff/admin or resource owner
    if resource.created_by != current_user.id and current_user.role not in [UserRole.STAFF, UserRole.ADMIN]:
        abort(403)
    
    if 'images' not in request.files:
        flash('No files provided.', 'error')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    files = request.files.getlist('images')
    if not files or not any(f.filename for f in files):
        flash('No files selected.', 'error')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    try:
        stored_paths = add_resource_images(resource_id, files)
        flash(f'Successfully uploaded {len(stored_paths)} image(s).', 'success')
    except ValueError as e:
        flash(f'Error uploading images: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))


@resources_bp.route('/<int:resource_id>/images/delete', methods=['POST'])
@login_required
def delete_image(resource_id):
    """Delete an image from a resource (staff/admin or resource owner only)."""
    resource = get_resource(resource_id)
    if not resource:
        abort(404)
    
    # Check permissions: staff/admin or resource owner
    if resource.created_by != current_user.id and current_user.role not in [UserRole.STAFF, UserRole.ADMIN]:
        abort(403)
    
    relative_path = request.form.get('image_path')
    if not relative_path:
        flash('No image path provided.', 'error')
        return redirect(url_for('resources.detail', resource_id=resource_id))
    
    try:
        remove_resource_image(resource_id, relative_path)
        flash('Image deleted successfully.', 'success')
    except ValueError as e:
        flash(f'Error deleting image: {str(e)}', 'error')
    except Exception as e:
        flash(f'Unexpected error: {str(e)}', 'error')
    
    return redirect(url_for('resources.detail', resource_id=resource_id))

