from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models import Car, CarMessage
from schemas import CarMessageCreateSchema, CarMessageSchema

messages_bp = Blueprint("messages", __name__)

create_schema = CarMessageCreateSchema()
message_schema = CarMessageSchema()
messages_schema = CarMessageSchema(many=True)


@messages_bp.post("/cars/<int:car_id>/messages")
def send_car_message(car_id):
    """Public — a buyer messages the seller of a specific car. No login required."""
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    try:
        data = create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    msg = CarMessage(
        car_id=car.id,
        seller_id=car.seller_id,
        buyer_name=data["name"],
        buyer_email=data["email"],
        message=data["message"],
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": "Your message has been sent to the seller."}), 201


@messages_bp.get("/messages")
@jwt_required()
def list_received_messages():
    """The logged-in seller's inbox — messages about cars they posted."""
    seller_id = int(get_jwt_identity())
    msgs = (
        CarMessage.query.filter_by(seller_id=seller_id)
        .order_by(CarMessage.created_at.desc())
        .all()
    )
    return jsonify(messages_schema.dump(msgs)), 200


@messages_bp.delete("/messages/<int:message_id>")
@jwt_required()
def delete_received_message(message_id):
    msg = CarMessage.query.get(message_id)
    if not msg:
        return jsonify({"error": "Message not found"}), 404
    if msg.seller_id != int(get_jwt_identity()):
        return jsonify({"error": "You can only delete your own messages"}), 403

    db.session.delete(msg)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200