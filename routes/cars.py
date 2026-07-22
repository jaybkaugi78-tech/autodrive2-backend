from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Car, User

cars_bp = Blueprint("cars", __name__, url_prefix="/cars")

REQUIRED_FIELDS = ["make", "model", "year", "price", "mileage"]


@cars_bp.get("")
def list_cars():
    cars = Car.query.order_by(Car.id.desc()).all()
    return jsonify([c.to_dict() for c in cars]), 200


@cars_bp.get("/<int:car_id>")
def get_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404
    return jsonify(car.to_dict()), 200


@cars_bp.post("")
@jwt_required()
def create_car():
    seller_id = int(get_jwt_identity())
    user = User.query.get(seller_id)
    if not user or user.role not in ("seller", "admin"):
        return jsonify({"error": "Only seller accounts can post listings"}), 403

    data = request.get_json() or {}
    missing = [f for f in REQUIRED_FIELDS if data.get(f) in (None, "")]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    car = Car(
        make=data["make"],
        model=data["model"],
        year=data["year"],
        price=data["price"],
        mileage=data["mileage"],
        image_url=data.get("image_url"),
        seller_id=seller_id,
    )
    db.session.add(car)
    db.session.commit()
    return jsonify(car.to_dict()), 201


@cars_bp.put("/<int:car_id>")
@jwt_required()
def update_car(car_id):
    car = Car.query.get(car_id)
    if not car:
        return jsonify({"error": "Car not found"}), 404

    current_user_id = int(get_jwt_identity())
    if car.seller_id != current_user_id:
        from models import User
        user = User.query.get(current_user_id)
        if not user or user.role != "admin":
            return jsonify({"error": "You can only edit your own listings"}), 403

    data = request.get_json() or {}
    for field in REQUIRED_FIELDS:
        if field in data:
            setattr(car, field, data[field])
    if "image_url" in data:
        car.image_url = data["image_url"]

    db.session.commit()
    return jsonify(car.to_dict()), 200


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
