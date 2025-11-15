"""AI Concierge service for natural language queries and reply drafting."""
import os
import datetime
import html
import re
from typing import List, Tuple
from pathlib import Path
from sqlalchemy import or_
from openai import OpenAI
from flask import current_app

from src.models.resource import Resource, ResourceStatus
from src.services.ai_client import extract_keywords

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_DISABLED = os.getenv("OPENAI_DISABLED", "0") == "1"

_client = OpenAI(api_key=OPENAI_API_KEY) if (OPENAI_API_KEY and not OPENAI_DISABLED) else None

# --- simple rate limit (memory; ok for MVP) ---
_last_call = {}  # {(user_id, endpoint): datetime}


def _rate_limit(user_id: int, key: str, seconds: int = 5):
    """Rate limit user requests."""
    now = datetime.datetime.utcnow()
    lk = (user_id, key)
    t = _last_call.get(lk)
    if t and (now - t).total_seconds() < seconds:
        raise ValueError("Please wait a few seconds before asking again.")
    _last_call[lk] = now


def _redact(text: str) -> str:
    """Basic PII/profanity guard for prompts."""
    text = re.sub(r"\b\d{3}[-.\s]?\d{2,3}[-.\s]?\d{4}\b", "[redacted-phone]", text)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "[redacted-email]", text)
    return text.strip()


def _resource_snippets(keywords: List[str], limit: int = 6) -> List[dict]:
    """
    Get resource snippets matching keywords with improved fuzzy matching.
    
    Enhanced to handle:
    - Synonym matching (quiet -> silent, study -> learning)
    - Capacity inference (1 person -> capacity 1-2)
    - Better relevance scoring
    """
    q = Resource.query.filter(Resource.status == ResourceStatus.PUBLISHED)
    
    # Extract capacity hints from keywords
    capacity_filter = None
    for kw in keywords:
        if 'individual' in kw or 'solo' in kw or 'single' in kw or '1person' in kw:
            capacity_filter = (1, 2)  # Capacity 1-2
        elif 'group' in kw or 'team' in kw or 'meeting' in kw:
            capacity_filter = (4, 100)  # Capacity 4+
    
    # Enhanced keyword synonyms for better matching
    synonym_map = {
        'quiet': ['quiet', 'silent', 'private', 'individual', 'solo'],
        'study': ['study', 'learning', 'reading', 'work', 'focus'],
        'music': ['music', 'instrument', 'practice', 'rehearsal', 'piano', 'vocal'],
        'meeting': ['meeting', 'conference', 'discussion', 'collaboration'],
        'group': ['group', 'team', 'collaborative', 'multiple'],
        'equipment': ['equipment', 'laptop', 'cart', 'device', 'technology'],
        'room': ['room', 'space', 'area', 'pod', 'booth'],
    }
    
    # Expand keywords with synonyms
    expanded_keywords = set()
    for keyword in keywords[:8]:
        expanded_keywords.add(keyword.lower())
        # Check if keyword matches any synonym group
        for key, synonyms in synonym_map.items():
            if keyword.lower() in synonyms or keyword.lower() == key:
                expanded_keywords.update(synonyms)
    
    if expanded_keywords:
        # Build OR conditions for each keyword
        conditions = []
        for t in expanded_keywords:
            cond = or_(
                Resource.title.ilike(f"%{t}%"),
                Resource.description.ilike(f"%{t}%"),
                Resource.category.ilike(f"%{t}%"),
                Resource.location.ilike(f"%{t}%"),
            )
            conditions.append(cond)
        
        # Combine with OR
        if conditions:
            q = q.filter(or_(*conditions))
    
    # Apply capacity filter if inferred
    if capacity_filter:
        min_cap, max_cap = capacity_filter
        q = q.filter(Resource.capacity >= min_cap, Resource.capacity <= max_cap)
    
    # Order by rating (higher rated resources first)
    q = q.order_by(Resource.rating_avg.desc(), Resource.created_at.desc())
    
    items = q.limit(limit).all()
    
    # If no results, try broader search (just category/location)
    if not items and keywords:
        q = Resource.query.filter(Resource.status == ResourceStatus.PUBLISHED)
        broad_conditions = []
        for t in keywords[:4]:
            broad_conditions.append(or_(
                Resource.category.ilike(f"%{t}%"),
                Resource.title.ilike(f"%{t}%")
            ))
        if broad_conditions:
            q = q.filter(or_(*broad_conditions))
        items = q.limit(limit).all()
    
    out = []
    for r in items:
        out.append({
            "id": r.id,
            "title": r.title,
            "category": r.category or "",
            "location": r.location or "",
            "capacity": r.capacity,
            "rating": r.rating_avg if r.rating_avg > 0 else None,
            "desc": (r.description or "")[:240]
        })
    return out


HELP_SYSTEM = (
    "You are the Campus Resource Hub AI Concierge. Be helpful, concise, and accurate.\n\n"
    "RULES:\n"
    "1. ONLY use data from the provided context - NEVER invent resource IDs, names, or details\n"
    "2. For 'discover' mode: Recommend 2-4 best matches from context list with specific details\n"
    "3. For 'help' mode: Explain processes clearly in numbered steps\n"
    "4. Match user needs intelligently:\n"
    "   - '1 person' or 'individual' → capacity 1-2\n"
    "   - 'quiet' or 'study' → study spaces, pods, individual rooms\n"
    "   - 'music' or 'practice' → music rooms, rehearsal spaces\n"
    "   - 'group' or 'meeting' → capacity 4+, meeting/conference rooms\n"
    "5. Include: title, location, capacity, rating (if available), and why it's a good match\n"
    "6. If no matches: say so clearly and suggest alternatives\n"
    "7. Keep answers under 150 words\n"
)


def _load_context_files():
    """
    Load context files from /docs/context/ to ground AI responses in project documentation.
    
    Returns:
        str: Combined context from project documentation files
    """
    try:
        # Get project root (assuming we're in src/services, go up 2 levels)
        project_root = Path(__file__).parent.parent.parent
        context_dir = project_root / "docs" / "context" / "shared"
        
        context_parts = []
        
        # Load key context files
        context_files = [
            "manual_test_plan.md",
            "security_reflection.md",
            "test_reflection.md"
        ]
        
        for filename in context_files:
            file_path = context_dir / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Truncate to first 500 chars to avoid token limits
                    context_parts.append(f"From {filename}:\n{content[:500]}...")
                except Exception as e:
                    current_app.logger.warning(f"Could not read context file {filename}: {e}")
        
        if context_parts:
            return "\n\n".join(context_parts)
        return ""
    except Exception as e:
        current_app.logger.warning(f"Error loading context files: {e}")
        return ""


def concierge_answer(user, query: str, mode: str = "help") -> Tuple[str, List[dict]]:
    """
    Answer user query using AI concierge.
    
    Args:
        user: Current user object
        query: User's question
        mode: "help" or "discover"
        
    Returns:
        Tuple of (answer text, list of resource snippets)
    """
    _rate_limit(user.id, "ask")
    q = _redact(query)
    
    # Build minimal context (RAG-lite) from DB for "discover"
    snippets = []
    kw = []
    
    if mode == "discover":
        kw = extract_keywords(q)
        snippets = _resource_snippets(kw, limit=6)
    
    # If API is disabled or missing, return a simple fallback answer
    if _client is None:
        if mode == "discover":
            if not snippets:
                return ("I couldn't find matching resources. Try different keywords.", [])
            lines = [
                f"- {s['title']} • {s.get('location') or 'N/A'} • cap: {s.get('capacity') or '—'} • ★ {s.get('rating') or '—'}"
                for s in snippets
            ]
            return ("Here are some matches:\n" + "\n".join(lines), snippets)
        # help mode fallback
        return (
            "You can find resources via the Resources page, then book. "
            "Pending means it awaits staff approval. Use filters for category/location.",
            []
        )
    
    # Construct messages
    user_role = getattr(user, 'role', None)
    if user_role and hasattr(user_role, 'value'):
        user_role = user_role.value
    else:
        user_role = 'student'
    user_ctx = f"User role: {user_role}. Today: {datetime.date.today().isoformat()}."
    context_blob = ""
    
    if snippets:
        context_blob = "Available resources matching your query:\n" + "\n".join([
            f"- Resource #{s['id']}: {s['title']}\n"
            f"  Category: {s['category']}, Location: {s['location']}\n"
            f"  Capacity: {s.get('capacity')} people, Rating: {s.get('rating') or 'Not yet rated'}\n"
            f"  Description: {s['desc']}"
            for s in snippets
        ])
    
    # Load project context files from /docs/context/ (required for context grounding)
    project_context = _load_context_files()
    
    messages = [
        {"role": "system", "content": HELP_SYSTEM},
        {"role": "system", "content": user_ctx},
    ]
    
    # Include project context if available (context grounding requirement)
    if project_context:
        messages.append({"role": "system", "content": f"Project Documentation Context:\n{project_context}"})
    
    messages.append({"role": "system", "content": context_blob or "No matching resources found in database for this query."})
    
    if mode == "discover":
        messages.append({
            "role": "user",
            "content": (
                f"User question: {q}\n\n"
                f"Task: Recommend the 2-4 BEST matching resources from the list above.\n"
                f"For each recommendation, explain:\n"
                f"- Resource name and location\n"
                f"- Capacity and rating\n"
                f"- Why it matches their needs\n\n"
                f"CRITICAL: Only recommend resources from the provided list. Do NOT invent resource IDs or names."
            )
        })
    else:
        messages.append({
            "role": "user",
            "content": f"User question: {q}\n\nProvide a clear, step-by-step answer about how to use the system."
        })
    
    try:
        resp = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2
        )
        answer = resp.choices[0].message.content.strip()
        return answer, snippets
    except Exception as e:
        current_app.logger.warning(f"OpenAI error in concierge_answer: {e}")
        # Fallback
        if mode == "discover" and snippets:
            lines = [
                f"- {s['title']} • {s.get('location') or 'N/A'} • cap: {s.get('capacity') or '—'}"
                for s in snippets
            ]
            return ("Here are some matches:\n" + "\n".join(lines), snippets)
        return ("I'm having trouble processing your request right now. Please try again later.", [])


def concierge_draft_reply(user, instruction: str) -> str:
    """
    Draft a polite reply message based on user instruction.
    
    Args:
        user: Current user object
        instruction: User's instruction for the draft
        
    Returns:
        Drafted reply text
    """
    _rate_limit(user.id, "draft")
    text = _redact(instruction)
    
    if _client is None:
        return (
            "(Draft – fallback)\nHello,\n\nThanks for your message. "
            "I'd be happy to help. Could you confirm the time window and any special requirements?\n\nBest regards,\n"
        )
    
    sys = (
        "You write short, polite, professional messages for campus bookings. "
        "Keep under 120 words, active voice, friendly tone. No PII."
    )
    
    messages = [
        {"role": "system", "content": sys},
        {"role": "user", "content": f"Write a reply based on this instruction:\n{text}"}
    ]
    
    try:
        resp = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.4
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        current_app.logger.warning(f"OpenAI error in concierge_draft_reply: {e}")
        return (
            "(Draft – fallback)\nHello,\n\nThanks for your message. "
            "I'd be happy to help. Could you confirm the time window and any special requirements?\n\nBest regards,\n"
        )

