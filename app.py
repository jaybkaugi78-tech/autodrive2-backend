from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, jwt
from routes.auth import auth_bp
from routes.cars import cars_bp
from routes.favorites import favorites_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(cars_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def health():
        return jsonify({"status": "ok", "service": "car-marketplace-api"}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
