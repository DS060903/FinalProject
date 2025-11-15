"""Flask application factory."""
import sys
import os

# Add parent directory to path to support running directly
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from dotenv import load_dotenv
load_dotenv()  # Load environment variables before other imports

from flask import Flask, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

from src.config import DevConfig, TestConfig, ProdConfig
from src.models import db, User

# Initialize extensions
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
csrf = CSRFProtect()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.query.get(int(user_id))


def create_app(config_name=None):
    """
    Application factory.
    
    Args:
        config_name: 'development', 'testing', or 'production' (defaults to env or 'development')
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__, template_folder='views', static_folder='static')
    
    # Determine config
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    config_map = {
        'development': DevConfig,
        'testing': TestConfig,
        'production': ProdConfig
    }
    
    app.config.from_object(config_map.get(config_name, DevConfig))
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    # Add CSRF token to template context
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=lambda: generate_csrf())
    
    # Register blueprints
    register_blueprints(app)
    
    # Exempt AI JSON endpoints from CSRF after blueprint registration
    # These endpoints use JSON and are protected by login_required instead
    from src.controllers.ai import assistant_ask, assistant_draft
    csrf.exempt(assistant_ask)
    csrf.exempt(assistant_draft)
    
    # Security headers
    @app.after_request
    def set_security_headers(resp):
        """Set security headers on all responses."""
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        # Simple, permissive CSP that still protects; adjust if you're using inline scripts
        resp.headers.setdefault("Content-Security-Policy",
            "default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net;")
        return resp
    
    # Register CLI commands
    register_commands(app)
    
    return app


def register_blueprints(app):
    """Register all blueprints."""
    from src.controllers.health import health_bp
    from src.controllers.auth import auth_bp
    from src.controllers.resources import resources_bp
    from src.controllers.bookings import bookings_bp
    from src.controllers.messaging import messaging_bp, messages_list_bp
    from src.controllers.reviews import reviews_bp
    from src.controllers.admin import admin_bp
    from src.controllers.ai import ai_bp
    
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(messages_list_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ai_bp)
    
    # Root route
    @app.route('/')
    def index():
        from flask import render_template
        from src.data_access.dal import list_resources as dal_list_resources, list_categories
        from src.models.resource import ResourceStatus
        
        # Get featured resources (published, top rated)
        resources = dal_list_resources({'sort': 'top_rated'}).limit(4).all()
        # Get categories for search dropdown
        categories = list_categories()
        return render_template('index.html', resources=resources, categories=categories)


def register_commands(app):
    """Register CLI commands."""
    @app.cli.command('seed')
    def seed():
        """Seed the database with comprehensive demo data."""
        from src.data_access.dal import (
            create_user, create_resource, create_booking, create_message,
            create_or_update_review, approve_booking, complete_booking,
            log_admin_action
        )
        from src.models.user import UserRole, User
        from src.models.resource import ResourceStatus, Resource
        from src.models.booking import BookingStatus, Booking
        from datetime import datetime, timedelta
        
        print("Seeding demo data...")
        
        # Create users with demo.edu domain
        try:
            admin = create_user('admin@demo.edu', 'Admin123!', UserRole.ADMIN)
            print(f"[OK] Created admin user: {admin.email}")
        except ValueError as e:
            admin = User.query.filter_by(email='admin@demo.edu').first()
            print(f"[INFO] Admin user already exists: {admin.email if admin else 'not found'}")
        
        try:
            staff = create_user('staff@demo.edu', 'Staff123!', UserRole.STAFF)
            print(f"[OK] Created staff user: {staff.email}")
        except ValueError as e:
            staff = User.query.filter_by(email='staff@demo.edu').first()
            print(f"[INFO] Staff user already exists: {staff.email if staff else 'not found'}")
        
        try:
            student = create_user('student@demo.edu', 'Student123!', UserRole.STUDENT)
            print(f"[OK] Created student user: {student.email}")
        except ValueError as e:
            student = User.query.filter_by(email='student@demo.edu').first()
            print(f"[INFO] Student user already exists: {student.email if student else 'not found'}")
        
        # Get users (create if needed)
        admin_user = User.query.filter_by(email='admin@demo.edu').first() or admin
        staff_user = User.query.filter_by(email='staff@demo.edu').first() or staff
        student_user = User.query.filter_by(email='student@demo.edu').first() or student
        
        if not admin_user or not staff_user or not student_user:
            print("❌ Error: Could not find required users for seeding")
            return
        
        # Create demo resources - only those with matching images
        demo_resources = [
            {
                'title': 'Study Pod 1',
                'description': 'Quiet study space for individual work',
                'category': 'Study Space',
                'location': 'Library, Floor 1',
                'capacity': 1,
                'status': ResourceStatus.PUBLISHED,
                'requires_approval': False,
                'created_by': staff_user.id
            },
            {
                'title': 'Laptop Cart',
                'description': 'Mobile cart with 15 laptops',
                'category': 'Equipment',
                'location': 'IT Department',
                'capacity': 15,
                'status': ResourceStatus.PUBLISHED,
                'requires_approval': True,
                'created_by': admin_user.id
            },
            {
                'title': 'Conference Room A',
                'description': 'Large conference room with projector, whiteboard, and video conferencing',
                'category': 'Room',
                'location': 'Building 1, Floor 2',
                'capacity': 20,
                'status': ResourceStatus.PUBLISHED,
                'requires_approval': True,
                'created_by': admin_user.id
            },
            {
                'title': 'Meeting Room B',
                'description': 'Small meeting room for 4-5 people',
                'category': 'Room',
                'location': 'Building 2, Floor 1',
                'capacity': 6,
                'status': ResourceStatus.PUBLISHED,
                'requires_approval': True,
                'created_by': staff_user.id
            }
        ]
        
        # Archive existing resources without images (to clean up old resources)
        # Archive ALL published resources without images, except our seed resources
        from src.models.resource import Resource
        
        seed_resource_titles = ['Study Pod 1', 'Laptop Cart', 'Conference Room A', 'Meeting Room B']
        resources_without_images = Resource.query.filter(
            (Resource.images.is_(None)) | (Resource.images == '[]')
        ).filter(
            Resource.status == ResourceStatus.PUBLISHED
        ).all()
        
        archived_count = 0
        for resource in resources_without_images:
            # Only archive if it's not one of our seed resources
            if resource.title not in seed_resource_titles:
                resource.status = ResourceStatus.ARCHIVED
                archived_count += 1
                print(f"[ARCHIVED] {resource.title} (no image)")
        
        if archived_count > 0:
            db.session.commit()
            print(f"[INFO] Archived {archived_count} resource(s) without images")
        
        created_resources = []
        # Map resources to available default images
        image_mapping = {
            'Study Pod 1': ['study-pod-1.png'],
            'Laptop Cart': ['laptop-cart.png'],
            'Conference Room A': ['conference-room-a.png'],
            'Meeting Room B': ['meeting-room-b.png']
        }
        
        for resource_data in demo_resources:
            resource_title = resource_data['title']
            try:
                # Check if resource already exists
                existing = db.session.query(Resource).filter_by(title=resource_title).first()
                
                if existing:
                    # Update existing resource to ensure it has an image
                    if resource_title in image_mapping:
                        existing.set_images(image_mapping[resource_title])
                        existing.status = ResourceStatus.PUBLISHED  # Ensure it's published
                        db.session.commit()
                        print(f"[OK] Updated resource: {existing.title} (assigned image)")
                    created_resources.append(existing)
                else:
                    # Create new resource
                    resource = create_resource(resource_data)
                    # Assign default image if available
                    if resource_title in image_mapping:
                        # Store image filename (will be loaded from static/img/)
                        resource.set_images(image_mapping[resource_title])
                        db.session.commit()
                    created_resources.append(resource)
                    print(f"[OK] Created resource: {resource.title}")
            except Exception as e:
                print(f"❌ Error creating/updating resource {resource_title}: {e}")
                # Try to get existing resource as fallback
                existing = db.session.query(Resource).filter_by(title=resource_title).first()
                if existing:
                    created_resources.append(existing)
                    print(f"[INFO] Using existing resource: {existing.title}")
        
        if not created_resources:
            print("❌ No resources available for booking creation")
            return
        
        # Create bookings with different statuses
        now = datetime.utcnow()
        study_pod = next((r for r in created_resources if 'Study Pod' in r.title), created_resources[0])
        laptop_cart = next((r for r in created_resources if 'Laptop' in r.title), created_resources[1])
        conference_room = next((r for r in created_resources if 'Conference' in r.title), created_resources[2])
        
        bookings_created = []
        pending_booking = None
        approved_booking = None
        completed_booking = None
        
        # Pending booking (needs approval)
        try:
            pending_start = now + timedelta(days=2)
            pending_end = pending_start + timedelta(hours=2)
            pending_booking = create_booking(
                student_user.id,
                laptop_cart.id,
                pending_start,
                pending_end
            )
            bookings_created.append(('pending', pending_booking))
            print(f"[OK] Created pending booking #{pending_booking.id} for {laptop_cart.title}")
        except Exception as e:
            print(f"[WARN] Could not create pending booking: {e}")
        
        # Approved booking
        try:
            approved_start = now + timedelta(days=3)
            approved_end = approved_start + timedelta(hours=3)
            approved_booking = create_booking(
                student_user.id,
                study_pod.id,
                approved_start,
                approved_end
            )
            if approved_booking and approved_booking.status == BookingStatus.PENDING:
                approve_booking(approved_booking.id, admin_user.id)
                approved_booking = db.session.query(Booking).get(approved_booking.id)
            if approved_booking:
                bookings_created.append(('approved', approved_booking))
                print(f"[OK] Created approved booking #{approved_booking.id} for {study_pod.title}")
        except Exception as e:
            print(f"[WARN] Could not create approved booking: {e}")
        
        # Completed booking (for reviews)
        try:
            completed_start = now - timedelta(days=5)
            completed_end = completed_start + timedelta(hours=2)
            completed_booking = create_booking(
                student_user.id,
                conference_room.id,
                completed_start,
                completed_end
            )
            if completed_booking:
                if completed_booking.status == BookingStatus.PENDING:
                    approve_booking(completed_booking.id, admin_user.id)
                    completed_booking = db.session.query(Booking).get(completed_booking.id)
                if completed_booking and completed_booking.status == BookingStatus.APPROVED:
                    complete_booking(completed_booking.id, admin_user.id)
                    completed_booking = db.session.query(Booking).get(completed_booking.id)
                if completed_booking:
                    bookings_created.append(('completed', completed_booking))
                    print(f"[OK] Created completed booking #{completed_booking.id} for {conference_room.title}")
        except Exception as e:
            print(f"[WARN] Could not create completed booking: {e}")
        
        # Create messages for bookings
        for status, booking in bookings_created:
            if booking and booking.status != BookingStatus.CANCELLED:
                try:
                    # Student message
                    msg1 = create_message(booking.id, student_user.id, 
                        f"Hello! I'd like to use this resource for my project. Is it available?")
                    print(f"[OK] Created message from student for booking #{booking.id}")
                    
                    # Owner/Admin reply
                    msg2 = create_message(booking.id, staff_user.id if booking.resource.created_by == staff_user.id else admin_user.id,
                        f"Hi! Yes, the resource is available. Please confirm your time slot.")
                    print(f"[OK] Created reply message for booking #{booking.id}")
                    
                    # Student follow-up
                    if status == 'pending':
                        msg3 = create_message(booking.id, student_user.id,
                            "Perfect! I'll be there at the scheduled time. Thank you!")
                        print(f"[OK] Created follow-up message for booking #{booking.id}")
                except Exception as e:
                    print(f"[WARN] Could not create messages for booking #{booking.id}: {e}")
        
        # Create reviews (only for completed bookings)
        completed_bookings = [b for status, b in bookings_created if status == 'completed' and b]
        review_data = [
            (5, "Excellent resource! The 3D printer worked perfectly for my project."),
            (4, "Great equipment, though the setup took a bit longer than expected."),
            (5, "Highly recommend! Very helpful staff and clean facility."),
        ]
        
        for i, booking in enumerate(completed_bookings[:3]):
            if booking:
                try:
                    rating, comment = review_data[i % len(review_data)]
                    create_or_update_review(
                        booking.resource_id,
                        student_user.id,
                        rating,
                        comment
                    )
                    print(f"[OK] Created review for resource #{booking.resource_id} (rating: {rating})")
                except Exception as e:
                    print(f"[WARN] Could not create review: {e}")
        
        # Create admin action logs
        try:
            log_admin_action(admin_user.id, 'booking_approved', f'Approved booking #{approved_booking.id if approved_booking else "N/A"}', '127.0.0.1')
            log_admin_action(admin_user.id, 'review_moderated', 'Reviewed and verified user reviews', '127.0.0.1')
            print("[OK] Created admin action logs")
        except Exception as e:
            print(f"[WARN] Could not create admin logs: {e}")
        
        print("\n[SUCCESS] Seeding completed successfully!")
        print("\nDemo Credentials:")
        print("   Admin:   admin@demo.edu / Admin123!")
        print("   Staff:   staff@demo.edu / Staff123!")
        print("   Student: student@demo.edu / Student123!")
        print("\nRun 'python src/app.py' or 'flask --app src.app run' to start the application!")
    
    @app.cli.command('seed-booking-demo')
    def seed_booking_demo():
        """Seed demo resources for booking workflow testing."""
        from src.data_access.dal import create_resource
        from src.models.resource import ResourceStatus
        
        # Use existing demo.edu users (created by main seed command)
        admin_user = User.query.filter_by(email='admin@demo.edu').first()
        if not admin_user:
            print("❌ Error: Please run 'flask --app src.app seed' first to create demo users")
            return
        
        staff_user = User.query.filter_by(email='staff@demo.edu').first()
        if not staff_user:
            print("❌ Error: Please run 'flask --app src.app seed' first to create demo users")
            return
        
        # Create open resource (auto-approve)
        open_resource = create_resource({
            'title': 'Open Meeting Room',
            'description': 'Automatically approved bookings - no approval needed',
            'category': 'Room',
            'location': 'Building 1, Floor 1',
            'capacity': 10,
            'status': ResourceStatus.PUBLISHED,
            'requires_approval': False,
            'created_by': staff_user.id
        })
        print(f"Created open resource: {open_resource.title} (auto-approve)")
        
        # Create restricted resource (requires approval)
        restricted_resource = create_resource({
            'title': 'Restricted Conference Room',
            'description': 'Requires staff/admin approval before booking is confirmed',
            'category': 'Room',
            'location': 'Building 2, Floor 3',
            'capacity': 25,
            'status': ResourceStatus.PUBLISHED,
            'requires_approval': True,
            'created_by': admin_user.id
        })
        print(f"Created restricted resource: {restricted_resource.title} (requires approval)")
        
        print("Booking demo resources seeded!")


# Allow running directly: python -m src.app or python src/app.py
if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='127.0.0.1', port=5000)
    

