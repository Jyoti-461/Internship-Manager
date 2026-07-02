"""
Authentication routes: single-page role-based login, student self-registration,
and logout. Teacher/admin accounts are NOT created here — only by an existing
admin via the admin dashboard (see routes/admin_routes.py).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import db
from models.user import User
from models.student import StudentProfile
from models.enquiry import ActivityLog
from utils.validators import is_valid_email, is_strong_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------------------
# LOGIN — single page, role selected via form field, same POST target
# ------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_dashboard_url_for(current_user.role))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role")  # 'student' | 'teacher' | 'admin'

        user = User.query.filter_by(email=email, role=role).first()

        if user is None or not user.check_password(password):
            flash("Invalid email, password, or role selected.", "error")
            return render_template("login.html")

        if not user.is_active:
            flash("This account has been deactivated. Contact the admin.", "error")
            return render_template("login.html")

        login_user(user)
        ActivityLog.log(user.id, "Logged in", f"role={user.role}")

        if user.must_reset_password:
            flash("Please reset your password before continuing.", "warning")
            return redirect(url_for("auth.reset_password"))

        return redirect(_dashboard_url_for(user.role))

    return render_template("login.html")


# ------------------------------------------------------------------
# REGISTER — students only (public). Teachers/admins are admin-created.
# ------------------------------------------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        college_name = request.form.get("college_name", "").strip()
        course = request.form.get("course", "").strip()
        phone = request.form.get("phone", "").strip()

        # --- validation ---
        if not full_name or not email or not password:
            flash("All required fields must be filled.", "error")
            return render_template("register.html")

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("register.html")

        if not is_strong_password(password):
            flash("Password must be at least 8 characters and include a letter and a number.", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        # --- create user + student profile ---
        new_user = User(full_name=full_name, email=email, role="student")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # get new_user.id before commit

        profile = StudentProfile(
            user_id=new_user.id,
            college_name=college_name,
            course=course,
            phone=phone,
        )
        db.session.add(profile)
        db.session.commit()

        ActivityLog.log(new_user.id, "Student registered", f"email={email}")

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


# ------------------------------------------------------------------
# FORCED PASSWORD RESET — for admin-created teacher/admin accounts
# ------------------------------------------------------------------
@auth_bp.route("/reset-password", methods=["GET", "POST"])
@login_required
def reset_password():
    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not is_strong_password(new_password):
            flash("Password must be at least 8 characters and include a letter and a number.", "error")
            return render_template("reset_password.html")

        if new_password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template("reset_password.html")

        current_user.set_password(new_password)
        current_user.must_reset_password = False
        db.session.commit()

        flash("Password updated successfully.", "success")
        return redirect(_dashboard_url_for(current_user.role))

    return render_template("reset_password.html")


@auth_bp.route("/logout")
@login_required
def logout():
    ActivityLog.log(current_user.id, "Logged out")
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))


def _dashboard_url_for(role):
    endpoint = {
        "student": "student.dashboard",
        "teacher": "teacher.dashboard",
        "admin": "admin.dashboard",
    }.get(role, "auth.login")
    return url_for(endpoint)
