from __future__ import annotations

import json

from flask import jsonify


def success_response(data: dict, status_code: int = 200):
    return jsonify(data), status_code


def format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
