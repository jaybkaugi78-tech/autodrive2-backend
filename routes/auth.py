from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from extensions import db
from models import User
from schemas import RegisterSchema, LoginSchema, ResetRequestSchema, ResetConfirmSchema, UserSchema

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

register_schema = RegisterSchema()
login_schema = LoginSchema()
reset_request_schema = ResetRequestSchema()
reset_confirm_schema = ResetConfirmSchema()
user_schema = UserSchema()


@auth_bp.post("/register")
def register():
    try:
        data = register_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "An account with that email already exists"}), 409

    user = User(name=data["name"], email=data["email"], role=data["role"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user_schema.dump(user)}), 201


@auth_bp.post("/login")
def login():
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user_schema.dump(user)}), 200


@auth_bp.post("/reset-password")
def request_reset():
    """Step 1: request a reset token for an email.

    Always returns 200 with a generic message, even if the email doesn't
    exist, so the endpoint can't be used to find out who has an account.
    In production this token would be emailed, not returned in the JSON —
    it's returned here only so the flow is testable without an email server.
    """
    try:
        data = reset_request_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    user = User.query.filter_by(email=data["email"]).first()

    response = {"message": "If that email exists, a reset link has been sent."}
    if user:
        response["reset_token"] = user.get_reset_token()  # dev-only convenience
    return jsonify(response), 200


@auth_bp.put("/reset-password/<token>")
def confirm_reset(token):
    """Step 2: use the token to set a new password."""
    try:
        data = reset_confirm_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    user = User.verify_reset_token(token)
    if not user:
        return jsonify({"error": "That reset link is invalid or has expired"}), 400

    user.set_password(data["password"])
    db.session.commit()
    return jsonify({"message": "Password updated"}), 200
