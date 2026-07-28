from flask import Blueprint, jsonify

from extensions import db
from models import User, Car, ContactMessage
from utils import admin_required
from schemas import UserSchema, CarSchema, ContactMessageSchema

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

users_schema = UserSchema(many=True)
car_schema = CarSchema()
contact_messages_schema = ContactMessageSchema(many=True)


@admin_bp.get("/users")
@admin_required
def list_users():
    users = User.query.order_by(User.id).all()
    return jsonify(users_schema.dump(users)), 200


@admin_bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.role == "admin":
        return jsonify({"error": "Cannot delete another admin account"}), 400

    db.session.delete(user)  
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

@admin_bp.get("/messages")
@admin_required
def list_messages():
    messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return jsonify(messages_schema.dump(messages)), 200


@admin_bp.delete("/messages/<int:message_id>")
@admin_required
def delete_message(message_id):
    msg = ContactMessage.query.get(message_id)
    if not msg:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(msg)
    db.session.commit()
    return jsonify({"message": "Message deleted"}), 200
