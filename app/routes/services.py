from datetime import UTC, datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db
from app.models import CloudService
from app.utils.errors import APIError
from app.utils.validators import require_fields, validate_enum, validate_url

services_bp = Blueprint("services", __name__, url_prefix="/api/services")

WRITABLE_FIELDS = {
    "name", "description", "service_type", "provider", "environment",
    "deployment_status", "health_status", "version",
    "repository_url", "service_url", "health_check_url",
}

FILTERABLE_FIELDS = {
    "environment", "provider", "health_status", "deployment_status", "service_type",
}


def _current_user_id() -> int:
    return int(get_jwt_identity())


def _get_owned_service(service_id: int):
    return CloudService.query.filter_by(
        id=service_id, user_id=_current_user_id()
    ).first()


def _validate_service_payload(data: dict) -> None:
    """Shared validation for create + update. Each helper is a no-op when the
    field is absent, so this works for partial updates too."""
    validate_enum(data.get("service_type"), CloudService.SERVICE_TYPES, "service_type")
    validate_enum(data.get("provider"), CloudService.PROVIDERS, "provider")
    validate_enum(data.get("environment"), CloudService.ENVIRONMENTS, "environment")
    validate_enum(
        data.get("deployment_status"), CloudService.DEPLOYMENT_STATUSES, "deployment_status"
    )
    validate_enum(data.get("health_status"), CloudService.HEALTH_STATUSES, "health_status")
    validate_url(data.get("repository_url"), "repository_url")
    validate_url(data.get("service_url"), "service_url")
    validate_url(data.get("health_check_url"), "health_check_url")


@services_bp.post("")
@jwt_required()
def create_service():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name"])
    _validate_service_payload(data)

    payload = {k: v for k, v in data.items() if k in WRITABLE_FIELDS}
    service = CloudService(user_id=_current_user_id(), **payload)
    db.session.add(service)
    db.session.commit()
    return jsonify({"service": service.to_dict()}), 201


@services_bp.get("")
@jwt_required()
def list_services():
    query = CloudService.query.filter_by(user_id=_current_user_id())
    for field in FILTERABLE_FIELDS:
        value = request.args.get(field)
        if value:
            query = query.filter_by(**{field: value})
    services = query.order_by(CloudService.created_at.desc()).all()
    return jsonify({
        "services": [s.to_dict() for s in services],
        "count": len(services),
    }), 200


@services_bp.get("/<int:service_id>")
@jwt_required()
def get_service(service_id):
    service = _get_owned_service(service_id)
    if service is None:
        raise APIError("Service not found", 404)
    return jsonify({"service": service.to_dict()}), 200


@services_bp.patch("/<int:service_id>")
@jwt_required()
def update_service(service_id):
    service = _get_owned_service(service_id)
    if service is None:
        raise APIError("Service not found", 404)

    data = request.get_json(silent=True) or {}
    _validate_service_payload(data)

    for field, value in data.items():
        if field in WRITABLE_FIELDS:
            setattr(service, field, value)

    db.session.commit()
    return jsonify({"service": service.to_dict()}), 200


@services_bp.delete("/<int:service_id>")
@jwt_required()
def delete_service(service_id):
    service = _get_owned_service(service_id)
    if service is None:
        raise APIError("Service not found", 404)

    db.session.delete(service)
    db.session.commit()
    return "", 204


@services_bp.patch("/<int:service_id>/health")
@jwt_required()
def update_health(service_id):
    """Manual health update — records status, response time, and timestamp."""
    service = _get_owned_service(service_id)
    if service is None:
        raise APIError("Service not found", 404)

    data = request.get_json(silent=True) or {}
    validate_enum(data.get("health_status"), CloudService.HEALTH_STATUSES, "health_status")

    if "health_status" in data:
        service.health_status = data["health_status"]
    if "response_time_ms" in data:
        service.response_time_ms = data["response_time_ms"]
    service.last_checked_at = datetime.now(UTC)

    db.session.commit()
    return jsonify({"service": service.to_dict()}), 200
