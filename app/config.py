import os

# Folder containing app/
APP_DIR = os.path.abspath(os.path.dirname(__file__))

# Project root (one level above app/)
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, ".."))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "syncspace_super_secret_key")

    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(BASE_DIR, 'database', 'database.db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(APP_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    CHAT_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER, "chat")
