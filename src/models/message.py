"""Message model."""
from datetime import datetime
from .user import db


class Message(db.Model):
    """Message model for booking-related communication."""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)  # Optional: who the message is directed to
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_hidden = db.Column(db.Boolean, nullable=False, default=False)
    is_reported = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationships (User model already defines sent_messages relationship with backref='sender')
    # Adding recipient relationship without backref to avoid conflicts
    recipient = db.relationship('User', foreign_keys=[recipient_id])
    
    def __repr__(self):
        return f'<Message {self.id} for Booking {self.booking_id}>'
    
    # Index for efficient querying by booking and time
    __table_args__ = (
        db.Index('idx_booking_created', 'booking_id', 'created_at'),
    )

