from flask import Blueprint, jsonify

from extensions import db
from models import User, Car
from utils import admin_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.role == "admin":
        return jsonify({"error": "Cannot delete another admin account"}), 400

    db.session.delete(user)  # cascades to their cars and favorites
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


@admin_bp.delete("/cars/<int:car_id>")
@admin_required
def admin_delete_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted"}), 200
