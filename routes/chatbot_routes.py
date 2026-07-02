"""
REST endpoint for the chatbot. The student-facing chat widget (static/js/chatbot.js)
POSTs each message here. This route:
  1. Finds or creates the student's active conversation.
  2. Saves the student's message.
  3. If the conversation is still bot-handled, runs it through bot_engine.
  4. Saves the bot's reply, and if escalate=True, creates an Enquiry + flips
     the conversation to 'escalated' so a teacher can pick it up.
  5. If the conversation has already been handed to a teacher (handled_by ==
     'teacher'), this route does NOT generate a bot reply — messages instead
     flow through the SocketIO live chat (see sockets/chat_events.py).
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from models import db
from models.chat import Conversation, Message
from models.enquiry import Enquiry
from utils.decorators import role_required
from chatbot.bot_engine import get_bot_response
from config import Config

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/api/chat/send", methods=["POST"])
@login_required
@role_required("student")
def send_message():
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # --- find or create the student's open conversation ---
    conversation = (
        Conversation.query
        .filter_by(student_id=current_user.id)
        .filter(Conversation.status.in_(["open", "escalated"]))
        .order_by(Conversation.created_at.desc())
        .first()
    )
    if conversation is None:
        conversation = Conversation(student_id=current_user.id, handled_by="bot", status="open")
        db.session.add(conversation)
        db.session.flush()

    # --- save student's message ---
    student_msg = Message(
        conversation_id=conversation.id,
        sender_type="student",
        sender_id=current_user.id,
        message_text=user_message,
    )
    db.session.add(student_msg)
    db.session.commit()

    # --- if already handed to a human teacher, don't run the bot ---
    if conversation.handled_by == "teacher":
        return jsonify({
            "conversation_id": conversation.id,
            "handled_by": "teacher",
            "message": "Your message has been sent to your assigned coordinator.",
        })

    # --- run the bot ---
    recent = Message.query.filter_by(conversation_id=conversation.id) \
        .order_by(Message.created_at.asc()).limit(20).all()
    recent_dicts = [{"sender_type": m.sender_type, "message_text": m.message_text} for m in recent]

    bot_result = get_bot_response(user_message, recent_dicts, model=Config.GEMINI_MODEL)

    bot_msg = Message(
        conversation_id=conversation.id,
        sender_type="bot",
        sender_id=None,
        message_text=bot_result["reply"],
    )
    db.session.add(bot_msg)

    if bot_result["escalate"]:
        conversation.status = "escalated"
        conversation.subject = bot_result.get("category", "General Enquiry")

        enquiry = Enquiry(
            conversation_id=conversation.id,
            student_id=current_user.id,
            category=bot_result.get("category", "Other"),
            summary=bot_result.get("summary", user_message[:150]),
            priority="medium",
            status="pending",
        )
        db.session.add(enquiry)

    db.session.commit()

    return jsonify({
        "conversation_id": conversation.id,
        "handled_by": conversation.handled_by,
        "reply": bot_result["reply"],
        "escalated": bot_result["escalate"],
        "source": bot_result["source"],
    })


@chatbot_bp.route("/api/chat/history", methods=["GET"])
@login_required
@role_required("student")
def chat_history():
    conversation = (
        Conversation.query
        .filter_by(student_id=current_user.id)
        .order_by(Conversation.created_at.desc())
        .first()
    )
    if conversation is None:
        return jsonify({"messages": [], "handled_by": "bot"})

    messages = Message.query.filter_by(conversation_id=conversation.id) \
        .order_by(Message.created_at.asc()).all()

    return jsonify({
        "conversation_id": conversation.id,
        "handled_by": conversation.handled_by,
        "messages": [m.to_dict() for m in messages],
    })
