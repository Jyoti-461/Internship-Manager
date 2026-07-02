"""
Main application entry point.

Run with:  python app.py
Make sure you've:
  1. Created the MySQL database (run database/schema.sql)
  2. Copied .env.example to .env and filled in your values
  3. Installed dependencies: pip install -r requirements.txt
"""

from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO

from config import Config
from models import db, bcrypt
from models.user import User

# Route blueprints
from routes.auth_routes import auth_bp
from routes.student_routes import student_bp
from routes.teacher_routes import teacher_bp
from routes.admin_routes import admin_bp
from routes.chatbot_routes import chatbot_bp

# SocketIO events
from sockets.chat_events import register_socket_events


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- init extensions ---
    db.init_app(app)
    bcrypt.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- register blueprints ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chatbot_bp)

    return app


app = create_app()
socketio = SocketIO(app, cors_allowed_origins="*")
register_socket_events(socketio)


def create_default_admin():
    """Seeds one admin account on first run if no admin exists yet."""
    with app.app_context():
        db.create_all()  # safe no-op if tables already exist (use schema.sql for full control)

        existing_admin = User.query.filter_by(role="admin").first()
        if existing_admin is None:
            admin = User(
                full_name="System Admin",
                email=Config.DEFAULT_ADMIN_EMAIL,
                role="admin",
                must_reset_password=True,
            )
            admin.set_password(Config.DEFAULT_ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()
            print(f"[startup] Default admin created: {Config.DEFAULT_ADMIN_EMAIL} / {Config.DEFAULT_ADMIN_PASSWORD}")
            print("[startup] You will be asked to reset this password on first login.")


if __name__ == "__main__":
    create_default_admin()
    socketio.run(app, debug=Config.DEBUG, host="0.0.0.0", port=5000)
