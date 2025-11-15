"""Notification service for booking events."""
from flask import current_app, flash


def send_notification(user_ids, subject, body):
    """
    Send a notification to users (simulated - logs and flashes).
    
    In production, this would send emails or push notifications.
    For now, it logs to the app logger and can add flash messages.
    
    Args:
        user_ids: List of user IDs to notify
        subject: Notification subject
        body: Notification body
    
    Returns:
        bool: True if successful
    """
    if not user_ids:
        return False
    
    # Log notification
    current_app.logger.info(f"Notification: {subject} | Recipients: {user_ids} | Body: {body}")
    
    # In a real implementation, you would:
    # - Send email via SMTP
    # - Send push notifications
    # - Store in database for in-app notifications
    # - Use a message queue for async processing
    
    # For now, we'll just log it
    # Flash messages are handled in controllers
    
    return True

