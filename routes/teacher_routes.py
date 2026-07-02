from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from models import db
from models.chat import Conversation
from models.enquiry import Enquiry, ActivityLog
from models.student import StudentProfile
from models.user import User
from utils.decorators import role_required

teacher_bp = Blueprint("teacher", __name__, url_prefix="/teacher")


@teacher_bp.route("/dashboard")
@login_required
@role_required("teacher")
def dashboard():
    pending_count = Enquiry.query.filter_by(status="pending").count()
    my_conversations_count = Conversation.query.filter_by(assigned_teacher_id=current_user.id).count()
    total_students = StudentProfile.query.count()

    return render_template(
        "teacher/dashboard.html",
        pending_count=pending_count,
        my_conversations_count=my_conversations_count,
        total_students=total_students,
    )


@teacher_bp.route("/enquiries")
@login_required
@role_required("teacher")
def enquiries():
    # Unassigned/escalated conversations any teacher can pick up
    unassigned = (
        Conversation.query
        .filter_by(status="escalated", assigned_teacher_id=None)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    # Conversations this teacher has already taken
    mine = (
        Conversation.query
        .filter_by(assigned_teacher_id=current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )
    return render_template("teacher/enquiries.html", unassigned=unassigned, mine=mine)


@teacher_bp.route("/enquiries/<int:conversation_id>/claim", methods=["POST"])
@login_required
@role_required("teacher")
def claim_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)

    if conversation.assigned_teacher_id is not None:
        flash("This conversation has already been claimed by another teacher.", "error")
        return redirect(url_for("teacher.enquiries"))

    conversation.assigned_teacher_id = current_user.id
    conversation.handled_by = "teacher"
    db.session.commit()

    ActivityLog.log(current_user.id, "Claimed conversation", f"conversation_id={conversation_id}")
    flash("Conversation assigned to you.", "success")
    return redirect(url_for("teacher.chat_reply", conversation_id=conversation_id))


@teacher_bp.route("/chat/<int:conversation_id>")
@login_required
@role_required("teacher")
def chat_reply(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)

    if conversation.assigned_teacher_id != current_user.id:
        flash("You are not assigned to this conversation.", "error")
        return redirect(url_for("teacher.enquiries"))

    return render_template("teacher/chat_reply.html", conversation=conversation)


@teacher_bp.route("/students")
@login_required
@role_required("teacher")
def students_list():
    students = (
        db.session.query(User, StudentProfile)
        .join(StudentProfile, User.id == StudentProfile.user_id)
        .filter(User.role == "student")
        .all()
    )
    return render_template("teacher/students_list.html", students=students)
