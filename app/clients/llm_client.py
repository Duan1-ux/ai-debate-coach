from __future__ import annotations

import json

import requests
from flask import current_app

from app.utils.errors import LLMClientError


class LLMClient:
    def __init__(self, config: dict):
        self.provider = config["LLM_PROVIDER"]
        self.api_base_url = config["LLM_API_BASE_URL"].rstrip("/")
        self.api_key = config["LLM_API_KEY"]
        self.model = config["LLM_MODEL"]
        self.timeout_seconds = config["LLM_TIMEOUT_SECONDS"]
        self.mock_chunk_size = config["MOCK_STREAM_CHUNK_SIZE"]

    def stream_debate_reply(self, messages: list[dict]):
        text = self.generate_debate_reply(messages)
        for index in range(0, len(text), self.mock_chunk_size):
            yield text[index : index + self.mock_chunk_size]

    def generate_debate_reply(self, messages: list[dict]) -> str:
        if self.provider == "mock" or not self.api_key:
            return self._mock_debate_reply(messages)
        return self._chat_completion(messages, temperature=0.7)

    def generate_evaluation(self, messages: list[dict]) -> str:
        if self.provider == "mock" or not self.api_key:
            return self._mock_evaluation(messages)
        return self._chat_completion(messages, temperature=0.2)

    def _chat_completion(self, messages: list[dict], temperature: float) -> str:
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.RequestException as exc:
            current_app.logger.exception("LLM request failed: %s", exc)
            raise LLMClientError("大模型服务调用失败，请稍后重试。") from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            current_app.logger.exception("Unexpected LLM response: %s", exc)
            raise LLMClientError("大模型返回格式异常。") from exc

    def _mock_debate_reply(self, messages: list[dict]) -> str:
        user_message = messages[-1]["content"].strip()
        topic = self._extract_topic(messages[0]["content"])
        snippet = user_message[:60]
        return (
            f"如果站在对方立场审视，你这段论证在“{topic}”上仍有明显缺口。"
            f"你强调了“{snippet}”，但没有证明这一判断为何必然成立，"
            "论据和因果链条之间也缺少关键连接。若核心前提无法自证，结论就更像态度表达而非完整论证。"
            "你需要补上可验证事实，并先回应最强反例。"
        )

    def _mock_evaluation(self, messages: list[dict]) -> str:
        content = {
            "logic_score": 7,
            "evidence_score": 6,
            "fluency_score": 7,
            "suggestion": "你的立场表达清楚，但论据还不够扎实。下一次训练优先补充可验证事实，并把“观点-理由-例证-结论”链条讲完整。",
        }
        return json.dumps(content, ensure_ascii=False)

    def _extract_topic(self, system_prompt: str) -> str:
        prefix = "本场辩题是："
        if prefix not in system_prompt:
            return "当前辩题"
        return system_prompt.split(prefix, maxsplit=1)[1].split("。", maxsplit=1)[0]
