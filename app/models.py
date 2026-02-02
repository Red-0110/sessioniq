from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from .extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    activities = db.relationship(
        "Activity",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    sessions = db.relationship(
        "Session",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(40), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    sessions = db.relationship(
        "Session",
        backref="activity",
        lazy=True,
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uq_activity_user_name"),
    )


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activity.id"), nullable=False, index=True)

    session_date = db.Column(db.Date, nullable=False, default=date.today, index=True)

    # Simple but useful MVP metrics:
    duration_min = db.Column(db.Integer, nullable=False)  # total minutes trained
    rpe = db.Column(db.Integer, nullable=False)  # 1-10 perceived effort
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def load(self) -> int:
        """Simple training load proxy."""
        return int(self.duration_min) * int(self.rpe)
