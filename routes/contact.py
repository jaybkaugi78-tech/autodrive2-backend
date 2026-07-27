from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from extensions import db
from models import ContactMessage
from schemas import ContactMessageCreateSchema

contact_bp = Blueprint("contact", __name__, url_prefix="/contact")

contact_create_schema = ContactMessageCreateSchema()


@contact_bp.post("")
def send_message():
    """Public endpoint — anyone can submit the Contact Us form, no login needed."""
    try:
        data = contact_create_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    msg = ContactMessage(name=data["name"], email=data["email"], message=data["message"])
    db.session.add(msg)
    db.session.commit()
    return jsonify({"message": "Thanks — your message has been sent."}), 201