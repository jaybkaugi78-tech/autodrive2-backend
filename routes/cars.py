from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models import Car, User
from schemas import CarSchema

cars_bp = Blueprint("cars", __name__, url_prefix="/cars")

car_schema = CarSchema()
cars_schema = CarSchema(many=True)


@cars_bp.get("")
def list_cars():
    cars = Car.query.order_by(Car.id.desc()).all()
    return jsonify(cars_schema.dump(cars)), 200


@cars_bp.get("/<int:car_id>")
def get_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    return jsonify(car_schema.dump(car)), 200


@cars_bp.post("")
@jwt_required()
def create_car():
    seller_id = int(get_jwt_identity())
    user = User.query.get(seller_id)
    if not user or user.role not in ("seller", "admin"):
        return jsonify({"error": "Only seller accounts can post listings"}), 403

    try:
        data = car_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    car = Car(seller_id=seller_id, **data)
    db.session.add(car)
    db.session.commit()
    return jsonify(car_schema.dump(car)), 201


@cars_bp.put("/<int:car_id>")
@jwt_required()
def update_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    current_user_id = int(get_jwt_identity())
    if car.seller_id != current_user_id:
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "You can only edit your own listings"}), 403

    try:
        data = car_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    for field, value in data.items():
        setattr(car, field, value)

    db.session.commit()
    return jsonify(car_schema.dump(car)), 200


@cars_bp.delete("/<int:car_id>")
@jwt_required()
def delete_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    if car.seller_id != int(get_jwt_identity()):
        return jsonify({"error": "You can only delete your own listings"}), 403

    db.session.delete(car)
    db.session.commit()
    return jsonify({"message": "Car deleted"}), 200
