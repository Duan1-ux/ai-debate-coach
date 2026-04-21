from __future__ import annotations

import json
import re

from app.schemas.evaluation import EvaluationResult


class EvaluationParser:
    DEFAULT_SCORE = 6
    DEFAULT_SUGGESTION = "评分格式异常，已返回默认分。建议下一次训练时进一步补强论据并优化表达结构。"

    def parse(self, raw_text: str) -> EvaluationResult:
        try:
            data = self._load_json(raw_text)
            return EvaluationResult(
                logic_score=self._coerce_score(
                    data.get("logic_score", data.get("logic"))
                ),
                evidence_score=self._coerce_score(
                    data.get("evidence_score", data.get("evidence"))
                ),
                fluency_score=self._coerce_score(
                    data.get("fluency_score", data.get("fluency"))
                ),
                suggestion=self._coerce_suggestion(data.get("suggestion")),
                fallback_used=False,
            )
        except Exception:
            return EvaluationResult(
                logic_score=self.DEFAULT_SCORE,
                evidence_score=self.DEFAULT_SCORE,
                fluency_score=self.DEFAULT_SCORE,
                suggestion=self.DEFAULT_SUGGESTION,
                fallback_used=True,
            )

    def _load_json(self, raw_text: str) -> dict:
        content = raw_text.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?", "", content)
            content = re.sub(r"```$", "", content).strip()

        if content.startswith("{") and content.endswith("}"):
            return json.loads(content)

        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise ValueError("No JSON object found in evaluation response.")

        return json.loads(match.group(0))

    def _coerce_score(self, value) -> int:
        if value is None:
            return self.DEFAULT_SCORE

        number = int(value)
        return max(0, min(10, number))

    def _coerce_suggestion(self, value) -> str:
        if not isinstance(value, str) or not value.strip():
            return self.DEFAULT_SUGGESTION
        return value.strip()
