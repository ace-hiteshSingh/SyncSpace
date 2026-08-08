import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, ".."))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    if not SECRET_KEY:
        SECRET_KEY = "dev-only-syncspace-secret-key"

    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        # Render/Postgres URLs may use postgres://.
        # SQLAlchemy expects postgresql://.
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1
            )

        SQLALCHEMY_DATABASE_URI = database_url
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"sqlite:///{os.path.join(BASE_DIR, 'database', 'database.db')}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.path.join(
        APP_DIR,
        "static",
        "uploads"
    )

    CHAT_UPLOAD_FOLDER = os.path.join(
        UPLOAD_FOLDER,
        "chat"
    )

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024