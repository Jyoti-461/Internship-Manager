import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file into environment variables


class Config:
    # --- Flask core ---
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-me")
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"

    # --- MySQL / SQLAlchemy ---
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "internship_portal")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Google Gemini API (free tier) ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # --- Default admin (used to auto-seed on first run) ---
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@firm.com")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@123")

    # --- File uploads (resumes) ---
    UPLOAD_FOLDER = os.path.join("static", "uploads", "resumes")
    ALLOWED_RESUME_EXTENSIONS = {"pdf", "doc", "docx"}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
