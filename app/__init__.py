from flask import Flask, jsonify

from app.config import get_config
from app.extensions import db, jwt


def create_app(config_name=None):
    """Application factory. Keeps the app importable for tests and CLI tools."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Initialise extensions
    db.init_app(app)
    jwt.init_app(app)

    # Import models so SQLAlchemy (and create_all) are aware of them
    from app.models import User, CloudService  # noqa: F401

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)

    # `flask init-db` — creates tables for local/dev use
    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        print("Database tables created.")

    # Make sure the API never returns an HTML error page
    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "Not found"}), 404

    return app
