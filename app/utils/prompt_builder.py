from __future__ import annotations


class PromptBuilder:
    def __init__(self, history_limit: int = 6, max_rounds: int = 3):
        self.history_limit = history_limit
        self.max_rounds = max_rounds

    def build_debate_messages(self, session, history: list, user_content: str) -> list[dict]:
        assistant_position = "反方" if session.position == "正方" else "正方"
        recent_history = history[-self.history_limit :]
        messages = [
            {
                "role": "system",
                "content": (
                    "你是一名严格、专业但克制的 AI 辩论陪练。"
                    f"本场辩题是：{session.topic}。"
                    f"用户持方是：{session.position}，你必须坚定扮演{assistant_position}。"
                    f"当前是第 {session.current_round + 1} / {self.max_rounds} 回合。"
                    "请直接给出有针对性的反驳，优先指出逻辑漏洞、论据不足和价值前提问题。"
                    "回复保持 120 到 220 字，语言自然，避免编号和寒暄。"
                ),
            }
        ]

        for item in recent_history:
            messages.append({"role": item.role, "content": item.content})

        messages.append({"role": "user", "content": user_content})
        return messages

    def build_evaluation_messages(self, session, history: list) -> list[dict]:
        transcript_lines = []
        for item in history:
            role_label = "用户" if item.role == "user" else "AI"
            transcript_lines.append(f"第{item.round_no}回合 {role_label}：{item.content}")

        transcript = "\n".join(transcript_lines)
        return [
            {
                "role": "system",
                "content": (
                    "你是一名专业辩论教练。"
                    "请只返回 JSON 对象，不要输出解释。"
                    "JSON 必须包含 logic_score、evidence_score、fluency_score、suggestion 四个字段。"
                    "前三项是 0 到 10 的整数。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"请根据以下 3 回合辩论记录，为用户生成评分。\n"
                    f"辩题：{session.topic}\n"
                    f"用户持方：{session.position}\n"
                    "评分维度：逻辑严密性、论据充实度、表达流畅性。\n"
                    "请重点指出下一次训练最值得改进的一件事。\n"
                    f"辩论记录：\n{transcript}"
                ),
            },
        ]
