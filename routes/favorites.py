from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models import Favorite, Car
from schemas import FavoriteCreateSchema, FavoriteSchema, CarSchema

favorites_bp = Blueprint("favorites", __name__, url_prefix="/favorites")

favorite_create_schema = FavoriteCreateSchema()
favorite_schema = FavoriteSchema()
cars_schema = CarSchema(many=True)


@favorites_bp.get("")
@jwt_required()
def list_favorites():
    user_id = int(get_jwt_identity())
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    cars = [Car.query.get(f.car_id) for f in favorites if Car.query.get(f.car_id)]
    return jsonify(cars_schema.dump(cars)), 200


@favorites_bp.post("")
@jwt_required()
def add_favorite():
    try:
        data = favorite_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    car_id = data["car_id"]
    if not Car.query.get(car_id):
        return jsonify({"error": "Car not found"}), 404

    user_id = int(get_jwt_identity())
    existing = Favorite.query.filter_by(user_id=user_id, car_id=car_id).first()
    if existing:
        return jsonify(favorite_schema.dump(existing)), 200

    favorite = Favorite(user_id=user_id, car_id=car_id)
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite_schema.dump(favorite)), 201


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
