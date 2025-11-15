"""Rate limiting service using in-memory token bucket."""
import time
from collections import defaultdict

# In-memory token bucket per (key, window); good enough for coursework
_hits = defaultdict(list)


def allow(key: str, limit: int, window_sec: int) -> bool:
    """
    Check if a request should be allowed based on rate limiting.
    
    Args:
        key: Unique identifier for the rate limit (e.g., IP address or user ID)
        limit: Maximum number of requests allowed
        window_sec: Time window in seconds
        
    Returns:
        True if request is allowed, False if rate limit exceeded
    """
    now = time.time()
    bucket = _hits[key]
    
    # Drop old entries outside the window
    while bucket and (now - bucket[0]) > window_sec:
        bucket.pop(0)
    
    # Check if limit exceeded
    if len(bucket) >= limit:
        return False
    
    # Add current request timestamp
    bucket.append(now)
    return True


def reset(key: str):
    """Reset rate limit for a given key (useful for testing)."""
    if key in _hits:
        del _hits[key]

