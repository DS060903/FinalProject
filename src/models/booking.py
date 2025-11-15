"""Booking model."""
from datetime import datetime
from .user import db
import enum


class BookingStatus(enum.Enum):
    """Booking status enumeration."""
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class Booking(db.Model):
    """Booking model for resource reservations."""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    start_dt = db.Column(db.DateTime, nullable=False, index=True)
    end_dt = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('Message', backref='booking', lazy='dynamic', foreign_keys='Message.booking_id')
    
    def __repr__(self):
        return f'<Booking {self.id} for Resource {self.resource_id}>'
    
    # Index for efficient conflict detection queries
    __table_args__ = (
        db.Index('idx_resource_time', 'resource_id', 'start_dt', 'end_dt'),
    )

