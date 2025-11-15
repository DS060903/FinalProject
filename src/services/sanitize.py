"""Text sanitization utilities."""

# List of words/phrases to filter (basic example)
_BLOCKED_WORDS = ["spam", "hack", "phish"]


def sanitize_body(text):
    """
    Sanitize message body text.
    
    Args:
        text: Raw message text
    
    Returns:
        Sanitized text (max 2000 chars)
    """
    if not text:
        return ""
    
    # Strip whitespace
    clean = text.strip()
    
    # Replace blocked words (case-insensitive)
    for bad_word in _BLOCKED_WORDS:
        # Case-insensitive replacement
        import re
        pattern = re.compile(re.escape(bad_word), re.IGNORECASE)
        clean = pattern.sub("***", clean)
    
    # Enforce max length
    if len(clean) > 2000:
        clean = clean[:2000]
    
    return clean

