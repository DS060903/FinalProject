"""Health check endpoints."""
from flask import Blueprint, jsonify
import os

health_bp = Blueprint('health', __name__)


@health_bp.route('/healthz', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@health_bp.route('/ai/health', methods=['GET'])
def ai_health():
    """AI service health check endpoint."""
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    disabled = os.getenv("OPENAI_DISABLED", "0") == "1"
    return jsonify({
        "ai_ready": bool(has_key and not disabled),
        "has_key": has_key,
        "disabled": disabled
    }), 200

