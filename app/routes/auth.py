from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.extensions import db, limiter
from app.models import User
from app.utils.errors import APIError
from app.utils.validators import require_fields

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
@limiter.limit("5 per minute")
def register():
    """Create a new account and return a JWT access token."""
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name", "email", "password"])

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    if len(password) < 8:
        raise APIError("Password must be at least 8 characters")

    if User.query.filter_by(email=email).first():
        raise APIError("A user with that email already exists", 409)

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    """Verify credentials and return a JWT access token."""
    data = request.get_json(silent=True) or {}
    require_fields(data, ["email", "password"])

    email = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        # Same message for both cases so we don't reveal which emails exist.
        raise APIError("Invalid email or password", 401)

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.get("/profile")
@jwt_required()
def profile():
    """Return the currently authenticated user. Requires a valid Bearer token."""
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=int(user_id)).first()
    if user is None:
        raise APIError("User not found", 404)
    return jsonify({"user": user.to_dict()}), 200
