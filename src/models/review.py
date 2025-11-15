"""Review model."""
from datetime import datetime
from .user import db


class Review(db.Model):
    """Review model for resource ratings and comments."""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey('resources.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    is_hidden = db.Column(db.Boolean, nullable=False, default=False)
    is_reported = db.Column(db.Boolean, nullable=False, default=False)
    
    # Ensure one review per user per resource
    __table_args__ = (
        db.UniqueConstraint('resource_id', 'user_id', name='uq_resource_user_review'),
        db.Index('idx_resource_created', 'resource_id', 'created_at'),
    )
    
    def __repr__(self):
        return f'<Review {self.id} for Resource {self.resource_id} by User {self.user_id}>'

