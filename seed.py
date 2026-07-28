from app import create_app
from extensions import db
from models import User, Car

def placeholder(make, model):
    label = f"{make} {model}".replace(" ", "+")
    return f"https://placehold.co/600x400/141414/d6ff3f?text={label}&font=raleway"


SAMPLE_CARS = [
    {"make": "Range Rover", "model": "Autobiography", "year": 2025, "price": 45000, "mileage": 10000,
     "image_url": "https://assets.onekeel.ai/images/2026/Land-Rover/Range-Rover/2026RangeRover-exterior-02.jpg",
     "fuel_type": "Petrol", "transmission": "Automatic", "horsepower": 523, "engine": "4.4L Twin-Turbo V8",
     "drivetrain": "AWD", "seats": 5, "zero_to_hundred": 4.6, "weight_kg": 2500, "fuel_consumption": "12.8L/100km",
     "description": "Flagship luxury SUV pairing serene ride comfort with genuine off-road capability and a first-class cabin."},
    {"make": "BMW", "model": "X7 xDrive 40i", "year": 2025, "price": 32400, "mileage": 7000,
     "image_url": "https://di-uploads-pod37.dealerinspire.com/bramanbmwmiami/uploads/2024/11/BMW-MY25-X7-CoreModels-Features-05-Desktop.jpg.bmwimg.small_-1024x768-1-1024x768.jpg",
     "fuel_type": "Petrol", "transmission": "Automatic", "horsepower": 375, "engine": "3.0L Twin-Turbo Inline-6",
     "drivetrain": "AWD", "seats": 7, "zero_to_hundred": 5.2, "weight_kg": 2300, "fuel_consumption": "9.6L/100km",
     "description": "A stealth-wealth living room on wheels — buttery-smooth turbo six in a massive, VIP-tier three-row fortress."},
    {"make": "Mercedes-Maybach", "model": "GLS 600", "year": 2025, "price": 70000, "mileage": 25000,
     "image_url": "https://carsforsale.co.ke/wp-content/uploads/2026/05/2025-Mercedes-Maybach-GLS-600-Night-Edition-ISG-4WD-Limited2.webp",
     "fuel_type": "Petrol", "transmission": "Automatic", "horsepower": 550, "engine": "4.0L Twin-Turbo V8",
     "drivetrain": "AWD", "seats": 5, "zero_to_hundred": 4.9, "weight_kg": 2700, "fuel_consumption": "13.5L/100km",
     "description": "The pinnacle of chauffeur-driven luxury — reclining rear captain's chairs and a whisper-quiet cabin."},
    {"make": "Volvo", "model": "S90 T8 Recharge", "year": 2024, "price": 8700, "mileage": 4500,
     "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSiuk2_IosujivnvcRALYlnoHIRp2jDIi3mquwz2Xds5JTB74YGXZDVFKdy&s=10",
     "fuel_type": "Hybrid", "transmission": "Automatic", "horsepower": 455, "engine": "2.0L Turbo + Electric Motor",
     "drivetrain": "AWD", "seats": 5, "zero_to_hundred": 4.7, "weight_kg": 2100, "fuel_consumption": "2.1L/100km",
     "description": "Understated Scandinavian luxury sedan with plug-in hybrid efficiency and a spa-like interior."},
    {"make": "Genesis", "model": "G80 3.5T", "year": 2025, "price": 17300, "mileage": 43000,
     "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbnwSQl3BzbshHzvj6AssK9XLiZa1gbG_BVZeo_jtbr9ZahNMAZglpTwg&s=10",
     "fuel_type": "Petrol", "transmission": "Automatic", "horsepower": 375, "engine": "3.5L Twin-Turbo V6",
     "drivetrain": "AWD", "seats": 5, "zero_to_hundred": 5.3, "weight_kg": 2000, "fuel_consumption": "11.2L/100km",
     "description": "A genuine alternative to the German mainstays, with a hand-finished cabin and effortless power."},
    {"make": "Volkswagen", "model": "Arteon R-Line", "year": 2021, "price": 5700, "mileage": 90000,
     "image_url": "https://cdn.motor1.com/images/mgl/RWK9e/s1/2020-vw-arteon-r-line-edition.webp",
     "fuel_type": "Petrol", "transmission": "Automatic", "horsepower": 300, "engine": "2.0L Turbo Inline-4",
     "drivetrain": "AWD", "seats": 5, "zero_to_hundred": 5.6, "weight_kg": 1700, "fuel_consumption": "8.9L/100km",
     "description": "Sleek fastback styling with hot-hatch punch, well cared for and ready for daily driving."},
    {"make": "Mercedes-Benz", "model": "190E", "year": 1990, "price": 400, "mileage": 190000,
     "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ6LC3CMIEp5UREw3pv286pl0rRx6nAChqEWYuTVDvABWTzBTuiZrHXQzj0&s=10",
     "fuel_type": "Petrol", "transmission": "Manual", "horsepower": 122, "engine": "2.0L Inline-4",
     "drivetrain": "RWD", "seats": 5, "zero_to_hundred": 10.5, "weight_kg": 1200, "fuel_consumption": "9.5L/100km",
     "description": "A tidy, honest classic — the compact Benz that built a reputation for over-engineering."},
    {"make": "BMW", "model": "E39 530d", "year": 1996, "price": 800, "mileage": 200000,
     "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbFDzYPENZtAqSoVWCh1dFS7GaRjRzWzjC_LYX-CDswg&s=10",
     "fuel_type": "Diesel", "transmission": "Manual", "horsepower": 193, "engine": "3.0L Inline-6 Turbodiesel",
     "drivetrain": "RWD", "seats": 5, "zero_to_hundred": 8.0, "weight_kg": 1600, "fuel_consumption": "7.8L/100km",
     "description": "Widely regarded as one of BMW's best-driving sedans ever built — high miles, still tight."},
    {"make": "Audi", "model": "80 B4", "year": 1993, "price": 600, "mileage": 200000,
     "image_url": "https://www.rdplastics.shop/cdn/shop/collections/photo_2024-07-28_02-47-02.jpg?v=1722378238",
     "fuel_type": "Petrol", "transmission": "Manual", "horsepower": 115, "engine": "2.0L Inline-4",
     "drivetrain": "FWD", "seats": 5, "zero_to_hundred": 11.2, "weight_kg": 1200, "fuel_consumption": "9.0L/100km",
     "description": "A dependable 90s workhorse — simple mechanicals, easy to maintain, built to outlast trends."},
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
