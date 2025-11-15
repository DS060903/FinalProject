"""Safe OpenAI wrapper for AI-powered features."""
import os
import logging
from typing import List
from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "15"))
OPENAI_DISABLED = os.getenv("OPENAI_DISABLED", "0") == "1"

_client = OpenAI(api_key=OPENAI_API_KEY) if (OPENAI_API_KEY and not OPENAI_DISABLED) else None


def extract_keywords(natural_query: str) -> List[str]:
    """
    Returns up to 8 concise keywords from a natural-language query.
    Enhanced with better fallback logic for common queries.
    """
    nq = (natural_query or "").strip()
    if not nq:
        return []
    
    # Enhanced fallback tokenization
    def fallback_keywords(query: str) -> List[str]:
        """Smarter fallback keyword extraction."""
        query_lower = query.lower()
        
        # Remove common stopwords
        stopwords = {'for', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of', 'with', 'by', 'is', 'are', 'can', 'i', 'my', 'me'}
        
        # Extract capacity numbers (e.g., "1 person" -> include "1")
        import re
        numbers = re.findall(r'\b\d+\b', query_lower)
        
        # Tokenize and filter
        words = query_lower.replace(",", " ").replace("?", " ").split()
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]
        
        # Add capacity keywords if found
        if numbers:
            keywords.extend([f"{n}person" for n in numbers if int(n) <= 20])
        
        # Handle common phrases
        if 'quiet' in query_lower or 'silent' in query_lower:
            keywords.extend(['quiet', 'study', 'individual'])
        if 'music' in query_lower:
            keywords.extend(['music', 'practice', 'instrument'])
        if 'group' in query_lower or 'meeting' in query_lower:
            keywords.extend(['meeting', 'conference', 'group'])
        
        return list(set(keywords))[:8]  # Remove duplicates
    
    if _client is None:
        return fallback_keywords(nq)
    
    try:
        resp = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": (
                    "Extract 5-8 search keywords from the query. Include:\n"
                    "- Main nouns (study, room, music, equipment)\n"
                    "- Key adjectives (quiet, large, private)\n"
                    "- Capacity hints (individual, group, solo, team)\n"
                    "Format: comma-separated, lowercase, no articles"
                )},
                {"role": "user", "content": nq}
            ],
            temperature=0.1,
            timeout=OPENAI_TIMEOUT
        )
        text = resp.choices[0].message.content.strip()
        parts = [p.strip().lower()[:40] for p in text.split(",") if p.strip()]
        return parts[:8] if parts else fallback_keywords(nq)
    except (APIConnectionError, RateLimitError, APIStatusError, Exception) as e:
        logging.warning(f"OpenAI unavailable, using fallback: {e}")
        return fallback_keywords(nq)
