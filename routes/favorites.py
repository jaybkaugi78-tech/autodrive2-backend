from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import db
from models import Favorite, Car

favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")


@favorites_bp.get("")
@jwt_required()
def list_favorites():
    user_id = int(get_jwt_identity())
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    cars = [Car.query.get(f.car_id).to_dict() for f in favorites if Car.query.get(f.car_id)]
    return jsonify(cars), 200


@favorites_bp.post("")
@jwt_required()
def add_favorite():
    data = request.get_json() or {}
    car_id = data.get("car_id")
    if not car_id:
        return jsonify({"error": "car_id is required"}), 400

    if not Car.query.get(car_id):
        return jsonify({"error": "Car not found"}), 404

    user_id = int(get_jwt_identity())
    existing = Favorite.query.filter_by(user_id=user_id, car_id=car_id).first()
    if existing:
        return jsonify(existing.to_dict()), 200

    favorite = Favorite(user_id=user_id, car_id=car_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.to_dict()), 201


@favorites_bp.delete("/<int:favorite_id>")
@jwt_required()
def remove_favorite(favorite_id):
    favorite = Favorite.query.get(favorite_id)
    if not favorite:
        return jsonify({"error": "Favorite not found"}), 404

    if favorite.user_id != int(get_jwt_identity()):
        return jsonify({"error": "You can only remove your own favorites"}), 403

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Removed from favorites"}), 200
