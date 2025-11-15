"""User model."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import enum

db = SQLAlchemy()


class UserRole(enum.Enum):
    """User role enumeration."""
    STUDENT = 'student'
    STAFF = 'staff'
    ADMIN = 'admin'


class User(UserMixin, db.Model):
    """User model with authentication and role-based access."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.STUDENT)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    resources = db.relationship('Resource', backref='creator', lazy='dynamic', foreign_keys='Resource.created_by')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic', foreign_keys='Booking.user_id')
    sent_messages = db.relationship('Message', backref='sender', lazy='dynamic', foreign_keys='Message.sender_id')
    reviews = db.relationship('Review', backref='user', lazy='dynamic', foreign_keys='Review.user_id')
    
    def __repr__(self):
        return f'<User {self.email}>'

