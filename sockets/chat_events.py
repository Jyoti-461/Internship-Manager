"""
Real-time chat between a student and their assigned teacher, once a
conversation has been escalated and claimed (handled_by == 'teacher').

Room naming convention: "conversation_<id>" — both the student's chat page
and the teacher's chat_reply page join this same room so messages broadcast
instantly to both sides.

Wire this up in app.py with:
    from sockets.chat_events import register_socket_events
    register_socket_events(socketio)
"""

from flask_socketio import join_room, leave_room, emit
from flask_login import current_user

from models import db
from models.chat import Conversation, Message


def register_socket_events(socketio):

    @socketio.on("join_conversation")
    def handle_join(data):
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            return
        room = f"conversation_{conversation_id}"
        join_room(room)
        emit("status", {"msg": "joined", "room": room})

    @socketio.on("leave_conversation")
    def handle_leave(data):
        conversation_id = data.get("conversation_id")
        if conversation_id:
            leave_room(f"conversation_{conversation_id}")

    @socketio.on("send_chat_message")
    def handle_send_message(data):
        """
        data: { conversation_id, message }
        Sender role/id comes from current_user (must be logged in via Flask-Login;
        Flask-SocketIO shares the session, so current_user works here too).
        """
        if not current_user.is_authenticated:
            emit("error", {"msg": "Not authenticated."})
            return

        conversation_id = data.get("conversation_id")
        text = (data.get("message") or "").strip()
        if not conversation_id or not text:
            return

        conversation = Conversation.query.get(conversation_id)
        if conversation is None:
            emit("error", {"msg": "Conversation not found."})
            return

        # Authorization: only the student who owns it or the assigned teacher can post
        is_owner_student = current_user.role == "student" and conversation.student_id == current_user.id
        is_assigned_teacher = current_user.role == "teacher" and conversation.assigned_teacher_id == current_user.id

        if not (is_owner_student or is_assigned_teacher):
            emit("error", {"msg": "Not authorized for this conversation."})
            return

        sender_type = "student" if current_user.role == "student" else "teacher"

        msg = Message(
            conversation_id=conversation_id,
            sender_type=sender_type,
            sender_id=current_user.id,
            message_text=text,
        )
        db.session.add(msg)
        db.session.commit()

        room = f"conversation_{conversation_id}"
        emit("new_message", msg.to_dict(), room=room)

    @socketio.on("mark_resolved")
    def handle_mark_resolved(data):
        """Teacher marks a conversation as resolved."""
        if not current_user.is_authenticated or current_user.role != "teacher":
            return

        conversation_id = data.get("conversation_id")
        conversation = Conversation.query.get(conversation_id)
        if conversation and conversation.assigned_teacher_id == current_user.id:
            conversation.status = "resolved"
            db.session.commit()
            room = f"conversation_{conversation_id}"
            emit("conversation_resolved", {"conversation_id": conversation_id}, room=room)
