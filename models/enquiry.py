from datetime import datetime
from models import db


class Enquiry(db.Model):
    __tablename__ = "enquiries"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id", ondelete="CASCADE"),
                                 nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = db.Column(db.String(100))
    summary = db.Column(db.Text)
    priority = db.Column(db.Enum("low", "medium", "high", name="priority_enum"), default="medium")
    status = db.Column(db.Enum("pending", "in_progress", "resolved", name="enquiry_status_enum"),
                        default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    student = db.relationship("User", foreign_keys=[student_id])
    conversation = db.relationship("Conversation")

    def __repr__(self):
        return f"<Enquiry {self.id} status={self.status}>"


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def log(user_id, action, details=""):
        entry = ActivityLog(user_id=user_id, action=action, details=details)
        db.session.add(entry)
        db.session.commit()
