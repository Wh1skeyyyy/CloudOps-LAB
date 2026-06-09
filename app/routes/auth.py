from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    """Create a new account and return a JWT access token."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({
            "error": "Validation error",
            "message": "name, email, and password are required",
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Validation error",
            "message": "Password must be at least 8 characters",
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({
            "error": "Conflict",
            "message": "A user with that email already exists",
        }), 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Identity must be a string for the JWT 'sub' claim (newer PyJWT enforces this).
    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    """Verify credentials and return a JWT access token."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({
            "error": "Validation error",
            "message": "email and password are required",
        }), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        # Same message for both cases so we don't reveal which emails exist.
        return jsonify({
            "error": "Unauthorized",
            "message": "Invalid email or password",
        }), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.get("/profile")
@jwt_required()
def profile():
    """Return the currently authenticated user. Requires a valid Bearer token."""
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=int(user_id)).first()
    if user is None:
        return jsonify({"error": "Not found", "message": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200
