from models import db


class StudentProfile(db.Model):
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False, unique=True)
    college_name = db.Column(db.String(150))
    course = db.Column(db.String(100))
    year_of_study = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    resume_path = db.Column(db.String(255))
    internship_domain = db.Column(db.String(100))
    application_status = db.Column(
        db.Enum("not_applied", "applied", "under_review", "accepted", "rejected",
                 name="application_status_enum"),
        default="not_applied"
    )

    def __repr__(self):
        return f"<StudentProfile user_id={self.user_id}>"
