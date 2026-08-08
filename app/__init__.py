from flask import Flask, jsonify, render_template, request
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError as SQLAlchemyOperationalError
from werkzeug.exceptions import RequestEntityTooLarge
from app.routes.profile import profile
from app.config import Config
from app.extensions import db, login_manager, migrate, socketio
from app.models.friend import Friend
from app.routes.auth import auth
from app.routes.dashboard import dashboard
from app.routes.friends import friends
from app.models.message import Message
from app.routes.chat import chat
from app.services.chat_service import ChatService
import app.sockets.chat_events


def ensure_user_json_columns(app):
    with app.app_context():
        db.create_all()

        inspector = inspect(db.engine)
        if not inspector.has_table("users"):
            return

        columns = {column["name"] for column in inspector.get_columns("users")}
        for column_name, column_sql in [
            ("tasks_json", "TEXT DEFAULT '[]'"),
            ("settings_json", "TEXT DEFAULT '{}'"),
            ("workspaces_json", "TEXT DEFAULT '[]'"),
        ]:
            if column_name not in columns:
                try:
                    db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_sql}"))
                except SQLAlchemyOperationalError as exc:
                    message = str(exc).lower()
                    if "duplicate column" in message or "already exists" in message:
                        continue
                    raise

        db.session.commit()


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)
    app.jinja_env.globals["format_chat_time"] = ChatService.format_time

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app)
    ensure_user_json_columns(app)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large_upload(error):
        if request.path.startswith("/chat/"):
            return jsonify(error="Files must be 20 MB or smaller."), 413
        return "Upload too large.", 413

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(profile)
    app.register_blueprint(friends)
    app.register_blueprint(chat)

    @app.route("/")
    def home():
        return render_template("landing/index.html")

    @app.route("/features")
    def features():
        return render_template("landing/features.html")

    @app.route("/getting-started")
    def getting_started():
        return render_template("landing/getting_started.html")

    return app
