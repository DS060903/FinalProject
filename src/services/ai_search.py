"""Smart search service using AI-powered keyword extraction."""
from sqlalchemy import or_
from ..models.resource import Resource, ResourceStatus
from .ai_client import extract_keywords


def smart_resource_query(user_query: str):
    """
    Perform smart search on resources using AI-extracted keywords.
    
    Args:
        user_query: Natural language search query from user
        
    Returns:
        tuple: (list of resources, comma-separated keywords string)
    """
    tokens = extract_keywords(user_query)
    q = Resource.query.filter(Resource.status == ResourceStatus.PUBLISHED)
    
    for t in tokens:
        cond = or_(
            Resource.title.ilike(f"%{t}%"),
            Resource.description.ilike(f"%{t}%"),
            Resource.category.ilike(f"%{t}%"),
            Resource.location.ilike(f"%{t}%"),
        )
        q = q.filter(cond)
    
    results = q.limit(30).all()
    return results, ", ".join(tokens)
