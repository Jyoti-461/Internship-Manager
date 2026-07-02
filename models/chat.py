from datetime import datetime
from models import db


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    assigned_teacher_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    handled_by = db.Column(db.Enum("bot", "teacher", name="handled_by_enum"), default="bot")
    status = db.Column(db.Enum("open", "escalated", "resolved", "closed", name="conv_status_enum"),
                        default="open")
    subject = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship("Message", backref="conversation",
                                cascade="all, delete-orphan",
                                order_by="Message.created_at")
    student = db.relationship("User", foreign_keys=[student_id])
    teacher = db.relationship("User", foreign_keys=[assigned_teacher_id])

    def __repr__(self):
        return f"<Conversation {self.id} student={self.student_id} handled_by={self.handled_by}>"


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"),
                                 nullable=False)
    sender_type = db.Column(db.Enum("student", "bot", "teacher", name="sender_type_enum"), nullable=False)
    sender_id = db.Column(db.Integer, nullable=True)  # NULL when sender_type == 'bot'
    message_text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "sender_type": self.sender_type,
            "sender_id": self.sender_id,
            "message_text": self.message_text,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
