from __future__ import annotations


def test_start_api(client):
    response = client.post(
        "/api/debate/start",
        json={"topic": "大学教育是否应该全面推行 AI 辅助学习", "position": "正方"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["session_id"]
    assert data["topic"] == "大学教育是否应该全面推行 AI 辅助学习"
    assert data["position"] == "正方"
    assert data["current_round"] == 0
