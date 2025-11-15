"""Admin log model for tracking admin actions."""
from datetime import datetime
from .user import db


class AdminLog(db.Model):
    """Admin log model for tracking administrative actions."""
    __tablename__ = 'admin_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(80), nullable=False, index=True)
    target_table = db.Column(db.String(80), nullable=True, index=True)
    target_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_addr = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship
    admin = db.relationship('User', backref='admin_logs', foreign_keys=[admin_id])
    
    def __repr__(self):
        return f'<AdminLog {self.id}: {self.action} by Admin {self.admin_id}>'

