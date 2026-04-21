from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(slots=True)
class EvaluationResult:
    logic_score: int
    evidence_score: int
    fluency_score: int
    suggestion: str
    fallback_used: bool = False

    def to_dict(self) -> dict:
        return asdict(self)
