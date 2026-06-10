from flask import Flask

from app.config import get_config
from app.extensions import db, jwt, limiter
from app.utils.errors import register_error_handlers


def create_app(config_name=None):
    """Application factory. Keeps the app importable for tests and CLI tools."""
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Initialise extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # Wire global error handlers (incl. JWT) so every error is consistent JSON
    register_error_handlers(app, jwt)

    # Import models so SQLAlchemy (and create_all) are aware of them
    from app.models import CloudService, User  # noqa: F401
    from app.routes.auth import auth_bp

    # Register blueprints
    from app.routes.health import health_bp
    from app.routes.services import services_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(services_bp)

    # `flask init-db` — creates tables for local/dev use
    @app.cli.command("init-db")
    def init_db():
        """Create all database tables."""
        db.create_all()
        print("Database tables created.")

    return app
