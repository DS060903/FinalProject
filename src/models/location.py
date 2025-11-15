"""Location model for resource physical locations."""
from datetime import datetime
from . import db


class Location(db.Model):
    """Resource location model."""
    
    __tablename__ = 'locations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to resources
    resources = db.relationship('Resource', back_populates='location_rel', lazy='dynamic')
    
    def __repr__(self):
        return f'<Location {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'building': self.building,
            'floor': self.floor,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

