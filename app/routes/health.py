from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    """Liveness probe — used by Docker healthchecks, Render, and uptime monitors."""
    return jsonify({"status": "healthy", "application": "CloudOps Lab"}), 200
