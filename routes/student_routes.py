import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db
from models.student import StudentProfile
from models.enquiry import ActivityLog
from utils.decorators import role_required
from utils.validators import allowed_resume_file
from config import Config

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template("student/dashboard.html", profile=profile)


@student_bp.route("/apply", methods=["GET", "POST"])
@login_required
@role_required("student")
def apply_internship():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        profile.internship_domain = request.form.get("internship_domain")
        profile.year_of_study = request.form.get("year_of_study")

        # --- handle resume upload ---
        resume_file = request.files.get("resume")
        if resume_file and resume_file.filename:
            if not allowed_resume_file(resume_file.filename, Config.ALLOWED_RESUME_EXTENSIONS):
                flash("Resume must be a PDF, DOC, or DOCX file.", "error")
                return render_template("student/apply_internship.html", profile=profile)

            os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(f"user{current_user.id}_{resume_file.filename}")
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            resume_file.save(filepath)
            profile.resume_path = filepath

        profile.application_status = "applied"
        db.session.commit()
        ActivityLog.log(current_user.id, "Submitted internship application")

        flash("Application submitted! You'll be notified once it's reviewed.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("student/apply_internship.html", profile=profile)


@student_bp.route("/chat")
@login_required
@role_required("student")
def chat():
    return render_template("student/chat.html")


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("student")
def profile():
    student_profile = StudentProfile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        current_user.full_name = request.form.get("full_name", current_user.full_name)
        student_profile.college_name = request.form.get("college_name")
        student_profile.course = request.form.get("course")
        student_profile.phone = request.form.get("phone")
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", profile=student_profile)
