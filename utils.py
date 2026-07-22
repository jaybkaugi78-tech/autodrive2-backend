from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import User


def admin_required(fn):
    """Runs after a valid JWT is confirmed, then checks the user's role.

    Stacks on top of the same JWT every other protected route uses —
    this isn't a separate auth system, just an extra permission check.
    """

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = User.query.get(int(get_jwt_identity()))
        if not user or user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return fn(*args, **kwargs)

    return wrapper
