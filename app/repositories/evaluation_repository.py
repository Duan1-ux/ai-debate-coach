from __future__ import annotations

from app.extensions import db
from app.models.evaluation import Evaluation


class EvaluationRepository:
    def get_by_session_id(self, session_id: str) -> Evaluation | None:
        return Evaluation.query.filter_by(session_id=session_id).first()

    def create(
        self,
        session_id: str,
        logic_score: int,
        evidence_score: int,
        fluency_score: int,
        suggestion: str,
    ) -> Evaluation:
        evaluation = Evaluation(
            session_id=session_id,
            logic_score=logic_score,
            evidence_score=evidence_score,
            fluency_score=fluency_score,
            suggestion=suggestion,
        )
        db.session.add(evaluation)
        return evaluation

    def save(self, evaluation: Evaluation) -> Evaluation:
        db.session.add(evaluation)
        return evaluation
