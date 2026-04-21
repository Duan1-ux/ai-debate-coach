from __future__ import annotations

from app.extensions import db
from app.repositories.session_repository import SessionRepository
from app.utils.errors import NotFoundError


class SessionService:
    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository

    def create_session(self, topic: str, position: str):
        session = self.session_repository.create(topic=topic, position=position)
        db.session.commit()
        return session

    def get_session_or_raise(self, session_id: str):
        session = self.session_repository.get_by_id(session_id)
        if session is None:
            raise NotFoundError("未找到对应的辩论会话。")
        return session
