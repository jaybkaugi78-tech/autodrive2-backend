from app import create_app
from extensions import db
from models import User, Car

SAMPLE_CARS = [
    {"make": "Range Rover", "model": "Autobiography", "year": 2025, "price": 45000, "mileage": 10000},
    {"make": "BMW", "model": "X7 xDrive 40i", "year": 2025, "price": 32400, "mileage": 7000},
    {"make": "Mercedes-Maybach", "model": "GLS 600", "year": 2025, "price": 70000, "mileage": 25000},
    {"make": "Volvo", "model": "S90 T8 Recharge", "year": 2024, "price": 8700, "mileage": 4500},
    {"make": "Genesis", "model": "G80 3.5T", "year": 2025, "price": 17300, "mileage": 43000},
    {"make": "Volkswagen", "model": "Arteon R-Line", "year": 2021, "price": 5700, "mileage": 90000},
    {"make": "Mercedes-Benz", "model": "190E", "year": 1990, "price": 400, "mileage": 190000},
    {"make": "BMW", "model": "E39 530d", "year": 1996, "price": 800, "mileage": 200000},
    {"make": "Audi", "model": "80 B4", "year": 1993, "price": 600, "mileage": 200000},
]

DEMO_SELLER_EMAIL = "demo.seller@carmarketplace.test"


def main():
    app = create_app()
    with app.app_context():
        if Car.query.count() > 0:
            print(f"Database already has {Car.query.count()} car(s) — skipping seed.")
            return

        seller = User.query.filter_by(email=DEMO_SELLER_EMAIL).first()
        if not seller:
            seller = User(name="Demo Seller", email=DEMO_SELLER_EMAIL, role="seller")
            seller.set_password("demopassword123")
            db.session.add(seller)
            db.session.commit()
            print(f"Created demo seller account ({DEMO_SELLER_EMAIL} / demopassword123)")

        for data in SAMPLE_CARS:
            db.session.add(Car(seller_id=seller.id, **data))
        db.session.commit()
        print(f"Added {len(SAMPLE_CARS)} sample cars.")


if __name__ == "__main__":
    main()