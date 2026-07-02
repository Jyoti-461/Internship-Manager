from datetime import datetime
from flask_login import UserMixin
from models import db, bcrypt


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("student", "teacher", "admin", name="role_enum"),
                      nullable=False, default="student")
    is_active_flag = db.Column("is_active", db.Boolean, default=True)
    must_reset_password = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student_profile = db.relationship("StudentProfile", backref="user", uselist=False,
                                       cascade="all, delete-orphan")
    teacher_profile = db.relationship("TeacherProfile", backref="user", uselist=False,
                                       cascade="all, delete-orphan")

    # --- Password helpers ---
    def set_password(self, plain_password):
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password):
        return bcrypt.check_password_hash(self.password_hash, plain_password)

    # --- Flask-Login required property ---
    @property
    def is_active(self):
        return self.is_active_flag

    # --- Convenience role checks ---
    def is_student(self):
        return self.role == "student"

    def is_teacher(self):
        return self.role == "teacher"

    def is_admin(self):
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
