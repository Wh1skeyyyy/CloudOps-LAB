from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.get("/")
def index():
    """Root endpoint — API info and a map of available routes.

    Gives the deployed base URL something meaningful to return (instead of a
    404), so it works as a live-demo link.
    """
    return jsonify({
        "name": "CloudOps Lab API",
        "description": "REST API for cataloguing and monitoring cloud services.",
        "status": "ok",
        "source": "https://github.com/Wh1skeyyyy/CloudOps-LAB",
        "endpoints": {
            "health": "GET /health",
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "profile": "GET /api/auth/profile",
            "services": "GET|POST /api/services",
            "service_detail": "GET|PATCH|DELETE /api/services/<id>",
            "service_health": "PATCH /api/services/<id>/health",
        },
    }), 200


@health_bp.get("/health")
def health():
    """Liveness probe — used by Docker healthchecks, Render, and uptime monitors."""
    return jsonify({"status": "healthy", "application": "CloudOps Lab"}), 200
