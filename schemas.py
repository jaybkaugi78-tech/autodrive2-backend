from marshmallow import Schema, fields, validate, ValidationError  

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class RegisterSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)
    role = fields.Str(validate=validate.OneOf(["buyer", "seller"]), load_default="buyer")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class ResetRequestSchema(Schema):
    email = fields.Email(required=True)


class ResetConfirmSchema(Schema):
    password = fields.Str(required=True, validate=validate.Length(min=8), load_only=True)


class CarSchema(Schema):
   

    id = fields.Int(dump_only=True)
    make = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    model = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    year = fields.Int(required=True, validate=validate.Range(min=1900, max=2100))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    mileage = fields.Int(required=True, validate=validate.Range(min=0))
    image_url = fields.Url(allow_none=True, load_default=None)

    fuel_type = fields.Str(allow_none=True, load_default=None, validate=validate.OneOf(
        ["Petrol", "Diesel", "Hybrid", "Electric"]))
    transmission = fields.Str(allow_none=True, load_default=None, validate=validate.OneOf(
        ["Automatic", "Manual"]))
    horsepower = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=0))
    engine = fields.Str(allow_none=True, load_default=None, validate=validate.Length(max=100))
    drivetrain = fields.Str(allow_none=True, load_default=None, validate=validate.OneOf(
        ["AWD", "RWD", "FWD"]))
    seats = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=1, max=20))
    zero_to_hundred = fields.Float(allow_none=True, load_default=None, validate=validate.Range(min=0))
    weight_kg = fields.Int(allow_none=True, load_default=None, validate=validate.Range(min=0))
    fuel_consumption = fields.Str(allow_none=True, load_default=None, validate=validate.Length(max=30))
    description = fields.Str(allow_none=True, load_default=None)

    seller_id = fields.Int(dump_only=True)


class FavoriteCreateSchema(Schema):
    car_id = fields.Int(required=True)


class FavoriteSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    car_id = fields.Int(dump_only=True)

class ContactMessageCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))


class ContactMessageSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    message = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class CarSummarySchema(Schema):
    id = fields.Int(dump_only=True)
    make = fields.Str(dump_only=True)
    model = fields.Str(dump_only=True)
    year = fields.Int(dump_only=True)


class CarMessageCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=2000))


class CarMessageSchema(Schema):
    id = fields.Int(dump_only=True)
    car = fields.Nested(CarSummarySchema, dump_only=True)
    buyer_name = fields.Str(dump_only=True)
    buyer_email = fields.Email(dump_only=True)
    message = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)