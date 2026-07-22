from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

from extensions import db

RESET_SALT = "password-reset"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="buyer")  # buyer or seller
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    cars = db.relationship("Car", backref="seller", lazy=True, cascade="all, delete-orphan")
    favorites = db.relationship("Favorite", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id}, salt=RESET_SALT)

    @staticmethod
    def verify_reset_token(token, max_age=1800):
        s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token, salt=RESET_SALT, max_age=max_age)
        except Exception:
            return None
        return User.query.get(data.get("user_id"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


class Car(db.Model):
    __tablename__ = "cars"

    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)

    fuel_type = db.Column(db.String(30), nullable=True)        # Petrol / Diesel / Hybrid / Electric
    transmission = db.Column(db.String(30), nullable=True)     # Automatic / Manual
    horsepower = db.Column(db.Integer, nullable=True)
    engine = db.Column(db.String(100), nullable=True)          # e.g. "3.0L Twin-Turbo Inline-6"
    drivetrain = db.Column(db.String(20), nullable=True)       # AWD / RWD / FWD
    seats = db.Column(db.Integer, nullable=True)
    zero_to_hundred = db.Column(db.Float, nullable=True)       # seconds
    weight_kg = db.Column(db.Integer, nullable=True)
    fuel_consumption = db.Column(db.String(30), nullable=True) # e.g. "9.6L/100km"
    description = db.Column(db.Text, nullable=True)

    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    listings = db.relationship("Listing", backref="car", lazy=True, cascade="all, delete-orphan")
    favorited_by = db.relationship("Favorite", backref="car", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "price": self.price,
            "mileage": self.mileage,
            "image_url": self.image_url,
            "fuel_type": self.fuel_type,
            "transmission": self.transmission,
            "horsepower": self.horsepower,
            "engine": self.engine,
            "drivetrain": self.drivetrain,
            "seats": self.seats,
            "zero_to_hundred": self.zero_to_hundred,
            "weight_kg": self.weight_kg,
            "fuel_consumption": self.fuel_consumption,
            "description": self.description,
            "seller_id": self.seller_id,
        }


class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    status = db.Column(db.String(20), default="active")  # active / sold / pending
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "car_id": self.car_id,
            "description": self.description,
            "status": self.status,
            "date_posted": self.date_posted.isoformat(),
        }


class Favorite(db.Model):
    __tablename__ = "favorites"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey("cars.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint("user_id", "car_id", name="unique_favorite"),)

    def to_dict(self):
        return {"id": self.id, "user_id": self.user_id, "car_id": self.car_id}