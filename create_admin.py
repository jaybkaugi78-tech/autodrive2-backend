"""
Create an admin account, or promote an existing user to admin.

Usage:
    python create_admin.py admin@example.com "Admin Name" somepassword

If the email already exists, that account is promoted to admin
(password left unchanged). Otherwise a new admin account is created.
"""
import sys
from app import create_app
from extensions import db
from models import User


def main():
    if len(sys.argv) != 4:
        print('Usage: python create_admin.py <email> "<name>" <password>')
        sys.exit(1)

    email, name, password = sys.argv[1], sys.argv[2], sys.argv[3]
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            user.role = "admin"
            db.session.commit()
            print(f"Promoted existing user {email} to admin.")
        else:
            user = User(name=name, email=email, role="admin")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"Created admin account for {email}.")


if __name__ == "__main__":
    main()
