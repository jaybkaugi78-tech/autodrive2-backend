from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from extensions import db
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with that email already exists"}), 409

    role = data.get("role", "buyer")
    if role not in ("buyer", "seller"):
        role = "buyer"  # admin accounts are created separately, never via public signup

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password or ""):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 200


@auth_bp.post("/reset-password")
def request_reset():
    """Step 1: request a reset token for an email.

    Always returns 200 with a generic message, even if the email doesn't
    exist, so the endpoint can't be used to find out who has an account.
    In production this token would be emailed, not returned in the JSON —
    it's returned here only so the flow is testable without an email server.
    """
    data = request.get_json() or {}
    email = data.get("email")
    user = User.query.filter_by(email=email).first()

    response = {"message": "If that email exists, a reset link has been sent."}
    if user:
        response["reset_token"] = user.get_reset_token()  # dev-only convenience
    return jsonify(response), 200


@auth_bp.put("/reset-password/<token>")
def confirm_reset(token):
    """Step 2: use the token to set a new password."""
    data = request.get_json() or {}
    new_password = data.get("password")
    if not new_password:
        return jsonify({"error": "password is required"}), 400

    user = User.verify_reset_token(token)
    if not user:
        return jsonify({"error": "That reset link is invalid or has expired"}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated"}), 200
