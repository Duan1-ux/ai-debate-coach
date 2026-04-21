from __future__ import annotations

from app.extensions import db
from app.models.message import Message


class MessageRepository:
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        round_no: int,
    ) -> Message:
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            round_no=round_no,
        )
        db.session.add(message)
        return message

    def list_by_session(self, session_id: str) -> list[Message]:
        return (
            Message.query.filter_by(session_id=session_id)
            .order_by(Message.id.asc())
            .all()
        )
