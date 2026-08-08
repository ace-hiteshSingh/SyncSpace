from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.extensions import db
from app.models.user import User


def register_user(username, email, password):
    """
    Register a new user.
    """

    username = (username or "").strip()
    email = (email or "").strip().lower()
    if len(username) < 3 or len(username) > 80:
        return False, "Username must be between 3 and 80 characters."
    if len(password or "") < 8:
        return False, "Password must be at least 8 characters."

    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()

    if existing_user:
        return False, "That email or username is already in use."

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return True, "Account created successfully."


def login_user_service(email, password):
    """
    Authenticate user.
    """

    user = User.query.filter_by(email=email).first()

    if not user:
        return None

    if not check_password_hash(user.password, password):
        return None

    return user
