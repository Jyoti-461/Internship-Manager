from models import db


class TeacherProfile(db.Model):
    __tablename__ = "teacher_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False, unique=True)
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))

    def __repr__(self):
        return f"<TeacherProfile user_id={self.user_id}>"
