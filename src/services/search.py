"""Search and filtering utilities for resources."""
from datetime import datetime, time, timedelta
from sqlalchemy import or_, and_, func, exists
from ..models import db
from ..models.resource import Resource
from ..models.booking import Booking, BookingStatus
from ..models.review import Review


def apply_resource_filters(query, filters):
    """
    Apply filters to a Resource query.
    
    Args:
        query: SQLAlchemy query object
        filters: dict with keys:
            - query: search term (searches title/description)
            - category: exact category match
            - location: location filter (partial match)
            - capacity_min: minimum capacity
            - date: optional date string (YYYY-MM-DD) - filters by availability_rules if present
            - status: ResourceStatus enum value or None (defaults to PUBLISHED if not specified)
            - sort: 'recent', 'most_booked', 'top_rated' (default: 'recent')
    
    Returns:
        Filtered query object
    """
    # Search query in title or description
    if filters.get('query'):
        search_term = f"%{filters['query']}%"
        query = query.filter(
            or_(
                Resource.title.ilike(search_term),
                Resource.description.ilike(search_term)
            )
        )
    
    # Category filter
    if filters.get('category'):
        query = query.filter(Resource.category == filters['category'])
    
    # Location filter (partial match)
    if filters.get('location'):
        location_term = f"%{filters['location']}%"
        query = query.filter(Resource.location.ilike(location_term))
    
    # Minimum capacity filter
    if filters.get('capacity_min') is not None:
        query = query.filter(Resource.capacity >= filters['capacity_min'])
    
    # Date filter (ensure resource has at least one open slot on the specified date)
    if filters.get('date'):
        try:
            filter_date = datetime.strptime(filters['date'], '%Y-%m-%d').date()
            day_start = datetime.combine(filter_date, time.min)
            day_end = day_start + timedelta(days=1)

            conflicting_booking_exists = exists().where(
                and_(
                    Booking.resource_id == Resource.id,
                    Booking.status.in_([BookingStatus.PENDING, BookingStatus.APPROVED]),
                    Booking.start_dt < day_end,
                    Booking.end_dt > day_start,
                )
            )

            query = query.filter(~conflicting_booking_exists)
        except ValueError:
            pass  # Invalid date format, skip filter
    
    # Status filter (default to PUBLISHED if not specified)
    status = filters.get('status')
    if status is None:
        from ..models.resource import ResourceStatus
        status = ResourceStatus.PUBLISHED
    query = query.filter(Resource.status == status)
    
    # Sorting
    sort_by = filters.get('sort', 'recent')
    if sort_by == 'most_booked':
        booking_counts = (
            db.session.query(
                Booking.resource_id.label('resource_id'),
                func.count(Booking.id).label('booking_count')
            )
            .filter(Booking.status.in_([BookingStatus.APPROVED, BookingStatus.COMPLETED]))
            .group_by(Booking.resource_id)
            .subquery()
        )

        query = (
            query.outerjoin(booking_counts, Resource.id == booking_counts.c.resource_id)
            .order_by(
                booking_counts.c.booking_count.desc().nullslast(),
                Resource.created_at.desc()
            )
        )
    elif sort_by == 'top_rated':
        # Sort by denormalized rating fields: rating_avg DESC, rating_count DESC, id DESC
        query = query.order_by(
            Resource.rating_avg.desc().nulls_last(),
            Resource.rating_count.desc(),
            Resource.id.desc()
        )
    else:  # default: recent (created_at desc)
        query = query.order_by(Resource.created_at.desc())
    
    return query

