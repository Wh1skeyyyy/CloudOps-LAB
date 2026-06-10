from datetime import UTC, datetime

from app.extensions import db


class CloudService(db.Model):
    __tablename__ = "cloud_services"

    # Allowed values live on the model so Phase 5 validators can reuse them.
    SERVICE_TYPES = ("frontend", "backend", "database", "worker", "container", "storage", "other")
    PROVIDERS = (
        "AWS", "Azure", "Google Cloud", "Render", "Railway", "Vercel", "Docker Local", "Other",
    )
    ENVIRONMENTS = ("development", "testing", "staging", "production")
    DEPLOYMENT_STATUSES = ("pending", "deploying", "successful", "failed", "rolled_back")
    HEALTH_STATUSES = ("healthy", "degraded", "down", "unknown")

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    service_type = db.Column(db.String(30), nullable=False, default="other")
    provider = db.Column(db.String(50), nullable=False, default="Other")
    environment = db.Column(db.String(30), nullable=False, default="development")

    deployment_status = db.Column(db.String(30), nullable=False, default="pending")
    health_status = db.Column(db.String(30), nullable=False, default="unknown")

    version = db.Column(db.String(30))
    repository_url = db.Column(db.String(255))
    service_url = db.Column(db.String(255))
    health_check_url = db.Column(db.String(255))

    response_time_ms = db.Column(db.Integer)
    last_checked_at = db.Column(db.DateTime)

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    owner = db.relationship("User", back_populates="services")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "service_type": self.service_type,
            "provider": self.provider,
            "environment": self.environment,
            "deployment_status": self.deployment_status,
            "health_status": self.health_status,
            "version": self.version,
            "repository_url": self.repository_url,
            "service_url": self.service_url,
            "health_check_url": self.health_check_url,
            "response_time_ms": self.response_time_ms,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
        }

    def __repr__(self) -> str:
        return f"<CloudService {self.name} ({self.environment})>"
