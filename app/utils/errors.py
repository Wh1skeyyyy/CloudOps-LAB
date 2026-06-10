from flask import jsonify


class APIError(Exception):
    """Raise this anywhere in the app to return a consistent JSON error.

    Example: raise APIError("name is required", 400)
    """

    DEFAULT_TITLES = {
        400: "Validation error",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not found",
        405: "Method not allowed",
        409: "Conflict",
        500: "Internal server error",
    }

    def __init__(self, message: str, status: int = 400, error: str | None = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.error = error or self.DEFAULT_TITLES.get(status, "Error")

    def to_response(self):
        return jsonify({"error": self.error, "message": self.message}), self.status


def register_error_handlers(app, jwt):
    """Wire up app-wide handlers so every error response is JSON with
    a consistent {error, message} shape. Replaces Flask's HTML pages and
    flask-jwt-extended's default {"msg": ...} format."""

    @app.errorhandler(APIError)
    def handle_api_error(err):
        return err.to_response()

    @app.errorhandler(404)
    def handle_404(_):
        return jsonify({"error": "Not found", "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def handle_405(_):
        return jsonify({
            "error": "Method not allowed",
            "message": "That HTTP method is not allowed on this URL",
        }), 405

    @app.errorhandler(500)
    def handle_500(_):
        return jsonify({
            "error": "Internal server error",
            "message": "Something went wrong",
        }), 500

    @app.errorhandler(429)
    def handle_429(err):
        return jsonify({
            "error": "Too many requests",
            "message": f"Rate limit exceeded ({err.description}). Try again later.",
        }), 429

    # JWT-specific responses
    @jwt.unauthorized_loader
    def jwt_missing(_reason):
        return jsonify({"error": "Unauthorized", "message": "Missing Authorization header"}), 401

    @jwt.invalid_token_loader
    def jwt_invalid(_reason):
        return jsonify({"error": "Unauthorized", "message": "Invalid token"}), 401

    @jwt.expired_token_loader
    def jwt_expired(_header, _payload):
        return jsonify({"error": "Unauthorized", "message": "Token has expired"}), 401
