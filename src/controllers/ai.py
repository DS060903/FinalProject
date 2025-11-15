"""AI Concierge controller."""
from flask import Blueprint, request, jsonify, render_template
from flask_login import current_user, login_required

from src.services.ai_concierge import concierge_answer, concierge_draft_reply

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")


@ai_bp.get("/assistant")
@login_required
def assistant_page():
    """Render the AI assistant page."""
    return render_template("ai/assistant.html")


@ai_bp.post("/assistant/ask")
@login_required
def assistant_ask():
    """Handle AI assistant query."""
    data = request.get_json() or {}
    q = (data.get("query") or "").strip()
    mode = (data.get("mode") or "help").strip()  # "help" | "discover"
    
    if not q:
        return jsonify({"error": "Empty query"}), 400
    
    try:
        answer, sources = concierge_answer(user=current_user, query=q, mode=mode)
        return jsonify({"answer": answer, "sources": sources}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        return jsonify({"error": "An error occurred processing your request"}), 500


@ai_bp.post("/assistant/draft")
@login_required
def assistant_draft():
    """Handle reply drafting request."""
    data = request.get_json() or {}
    prompt = (data.get("prompt") or "").strip()
    
    if not prompt:
        return jsonify({"error": "Empty prompt"}), 400
    
    try:
        draft = concierge_draft_reply(user=current_user, instruction=prompt)
        return jsonify({"draft": draft}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 429
    except Exception as e:
        return jsonify({"error": "An error occurred processing your request"}), 500

