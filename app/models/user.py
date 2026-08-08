from datetime import datetime

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    # ==========================
    # Profile Information
    # ==========================

    bio = db.Column(
        db.Text,
        default=""
    )

    location = db.Column(
        db.String(100),
        default=""
    )

    website = db.Column(
        db.String(255),
        default=""
    )

    tasks_json = db.Column(
        db.Text,
        default="[]"
    )

    settings_json = db.Column(
        db.Text,
        default="{}"
    )

    workspaces_json = db.Column(
        db.Text,
        default="[]"
    )

    avatar = db.Column(
        db.String(255),
        default="default-avatar.png"
    )

    # ==========================
    # Status
    # ==========================

    is_online = db.Column(
        db.Boolean,
        default=False
    )

    last_seen = db.Column(
        db.DateTime,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.username}>"