from __future__ import annotations

from datetime import UTC, datetime

from app.extensions import db


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(
        db.String(36),
        db.ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    round_no = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    session = db.relationship("Session", back_populates="messages")
