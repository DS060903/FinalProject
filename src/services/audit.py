"""Audit logging utilities for admin actions."""
from flask import request


def capture_ip(request_obj):
    """
    Capture IP address from request, handling proxies.
    
    Args:
        request_obj: Flask request object
    
    Returns:
        str: IP address
    """
    if not request_obj:
        return None
    
    # Check for X-Forwarded-For header (proxy/load balancer)
    forwarded_for = request_obj.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(',')[0].strip()
    
    # Fallback to remote_addr
    return request_obj.remote_addr


def record_admin_action(admin_id, action, target_table, target_id, details="", request_obj=None):
    """
    Record an admin action to the audit log.
    
    Args:
        admin_id: ID of admin performing the action
        action: Action name (e.g., "approve_booking", "hide_message")
        target_table: Table name (e.g., "bookings", "messages")
        target_id: ID of the target record
        details: Additional details (optional)
        request_obj: Flask request object for IP capture (optional)
    """
    from ..data_access.dal import log_admin_action
    
    ip_addr = capture_ip(request_obj) if request_obj else None
    log_admin_action(admin_id, action, target_table, target_id, details, ip_addr)

