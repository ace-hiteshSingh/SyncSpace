from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

# Database
db = SQLAlchemy()

# Login Manager
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login first."
login_manager.login_message_category = "error"

# Database Migrations
migrate = Migrate()

# Socket.IO
socketio = SocketIO()


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User

    return User.query.get(int(user_id))