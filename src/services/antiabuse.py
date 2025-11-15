"""Anti-abuse utilities for messaging."""
from datetime import datetime, timedelta
from collections import defaultdict

# Simple in-memory cooldown tracker
# In production, use Redis or similar distributed cache
_cooldown_cache = defaultdict(dict)


def check_cooldown(user_id, booking_id, seconds=10):
    """
    Check if user can post a message (cooldown check).
    
    Args:
        user_id: User ID
        booking_id: Booking ID
        seconds: Cooldown period in seconds (default: 10)
    
    Raises:
        ValueError: If user is still in cooldown period
    
    Returns:
        None if cooldown check passes
    """
    key = f"{user_id}:{booking_id}"
    now = datetime.utcnow()
    
    if key in _cooldown_cache:
        last_post_time = _cooldown_cache[key]
        time_since_last = (now - last_post_time).total_seconds()
        
        if time_since_last < seconds:
            remaining = seconds - time_since_last
            raise ValueError(f"Please wait {remaining:.1f} seconds before posting another message.")
    
    # Update cooldown cache
    _cooldown_cache[key] = now
    
    # Clean up old entries (older than cooldown period)
    # This prevents memory leak
    cutoff_time = now - timedelta(seconds=seconds * 2)
    keys_to_remove = [
        k for k, v in _cooldown_cache.items()
        if v < cutoff_time
    ]
    for k in keys_to_remove:
        del _cooldown_cache[k]


def clear_cooldown(user_id, booking_id):
    """
    Clear cooldown for a user/booking (useful for testing).
    
    Args:
        user_id: User ID
        booking_id: Booking ID
    """
    key = f"{user_id}:{booking_id}"
    if key in _cooldown_cache:
        del _cooldown_cache[key]

