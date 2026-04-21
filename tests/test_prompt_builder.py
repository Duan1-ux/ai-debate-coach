from __future__ import annotations

from types import SimpleNamespace

from app.utils.prompt_builder import PromptBuilder


def test_prompt_builder():
    builder = PromptBuilder(history_limit=4, max_rounds=3)
    session = SimpleNamespace(topic="安乐死是否应该合法化", position="正方", current_round=1)
    history = [
        SimpleNamespace(role="user", content="我方认为应尊重患者自主。", round_no=1),
        SimpleNamespace(role="assistant", content="自主并不意味着社会可放弃保护生命。", round_no=1),
    ]

    messages = builder.build_debate_messages(
        session=session,
        history=history,
        user_content="制度设计可以配合严格审核。",
    )

    assert messages[0]["role"] == "system"
    assert "安乐死是否应该合法化" in messages[0]["content"]
    assert "反方" in messages[0]["content"]
    assert messages[-1]["content"] == "制度设计可以配合严格审核。"
    assert len(messages) == 4
