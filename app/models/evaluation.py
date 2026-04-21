from __future__ import annotations

from datetime import UTC, datetime

from app.extensions import db


def utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(
        db.String(36),
        db.ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    logic_score = db.Column(db.Integer, nullable=False)
    evidence_score = db.Column(db.Integer, nullable=False)
    fluency_score = db.Column(db.Integer, nullable=False)
    suggestion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    session = db.relationship("Session", back_populates="evaluation")
