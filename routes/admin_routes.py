import secrets
import string

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.user import User
from models.teacher import TeacherProfile
from models.student import StudentProfile
from models.enquiry import Enquiry, ActivityLog
from models.chat import Conversation
from utils.decorators import role_required
from utils.validators import is_valid_email

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    total_students = User.query.filter_by(role="student").count()
    total_teachers = User.query.filter_by(role="teacher").count()
    pending_enquiries = Enquiry.query.filter_by(status="pending").count()
    open_conversations = Conversation.query.filter(Conversation.status.in_(["open", "escalated"])).count()

    return render_template(
        "admin/dashboard.html",
        total_students=total_students,
        total_teachers=total_teachers,
        pending_enquiries=pending_enquiries,
        open_conversations=open_conversations,
    )


@admin_bp.route("/manage-users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def manage_users():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role")  # 'teacher' or 'admin'
        department = request.form.get("department", "").strip()
        designation = request.form.get("designation", "").strip()

        if role not in ("teacher", "admin"):
            flash("Invalid role selected.", "error")
            return redirect(url_for("admin.manage_users"))

        if not full_name or not is_valid_email(email):
            flash("Please provide a valid name and email.", "error")
            return redirect(url_for("admin.manage_users"))

        if User.query.filter_by(email=email).first():
            flash("A user with this email already exists.", "error")
            return redirect(url_for("admin.manage_users"))

        # Generate a temporary random password; the user must reset it on first login.
        temp_password = _generate_temp_password()

        new_user = User(full_name=full_name, email=email, role=role, must_reset_password=True)
        new_user.set_password(temp_password)
        db.session.add(new_user)
        db.session.flush()

        if role == "teacher":
            db.session.add(TeacherProfile(user_id=new_user.id, department=department, designation=designation))

        db.session.commit()
        ActivityLog.log(current_user.id, f"Created {role} account", f"email={email}")

        flash(
            f"{role.title()} account created for {email}. "
            f"Temporary password: {temp_password} (share this securely — it will not be shown again).",
            "success",
        )
        return redirect(url_for("admin.manage_users"))

    teachers = User.query.filter_by(role="teacher").all()
    admins = User.query.filter_by(role="admin").all()
    return render_template("admin/manage_users.html", teachers=teachers, admins=admins)


@admin_bp.route("/manage-users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@role_required("admin")
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot deactivate your own account.", "error")
        return redirect(url_for("admin.manage_users"))

    user.is_active_flag = not user.is_active_flag
    db.session.commit()
    ActivityLog.log(current_user.id, "Toggled user active status", f"user_id={user_id} -> {user.is_active_flag}")
    flash(f"{user.email} is now {'active' if user.is_active_flag else 'deactivated'}.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/analytics")
@login_required
@role_required("admin")
def analytics():
    status_breakdown = (
        db.session.query(StudentProfile.application_status, db.func.count(StudentProfile.id))
        .group_by(StudentProfile.application_status)
        .all()
    )
    enquiry_breakdown = (
        db.session.query(Enquiry.category, db.func.count(Enquiry.id))
        .group_by(Enquiry.category)
        .all()
    )
    return render_template(
        "admin/analytics.html",
        status_breakdown=status_breakdown,
        enquiry_breakdown=enquiry_breakdown,
    )


@admin_bp.route("/logs")
@login_required
@role_required("admin")
def logs():
    recent_logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(200).all()
    return render_template("admin/logs.html", logs=recent_logs)


def _generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
