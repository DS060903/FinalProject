"""Resource model."""
from datetime import datetime
from .user import db
import enum
import json


class ResourceStatus(enum.Enum):
    """Resource status enumeration."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'


class Resource(db.Model):
    """Resource model for bookable items."""
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # New foreign key fields (DB-driven)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=True, index=True)
    
    # Legacy string fields (deprecated, kept for backward compatibility)
    category = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    
    capacity = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Enum(ResourceStatus), nullable=False, default=ResourceStatus.DRAFT, index=True)
    requires_approval = db.Column(db.Boolean, nullable=False, default=False)
    availability_rules = db.Column(db.Text, nullable=True)  # JSON stored as text
    images = db.Column(db.Text, nullable=True)  # JSON array of relative image paths
    rating_avg = db.Column(db.Float, nullable=False, default=0.0)
    rating_count = db.Column(db.Integer, nullable=False, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='resource', lazy='dynamic', foreign_keys='Booking.resource_id')
    reviews = db.relationship('Review', backref='resource', lazy='dynamic', foreign_keys='Review.resource_id')
    category_rel = db.relationship('Category', back_populates='resources')
    location_rel = db.relationship('Location', back_populates='resources')
    # Note: 'creator' backref is defined in User model via resources relationship
    
    def __repr__(self):
        return f'<Resource {self.title}>'
    
    def get_availability_rules(self):
        """Parse availability_rules JSON if present."""
        if self.availability_rules:
            try:
                return json.loads(self.availability_rules)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_availability_rules(self, rules_dict):
        """Store availability_rules as JSON."""
        self.availability_rules = json.dumps(rules_dict) if rules_dict else None
    
    def get_images(self):
        """Parse images JSON array if present."""
        if self.images:
            try:
                return json.loads(self.images)
            except json.JSONDecodeError:
                return []
        return []
    
    def set_images(self, images_list):
        """Store images as JSON array."""
        self.images = json.dumps(images_list) if images_list else None

