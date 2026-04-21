# Frontend Handoff

This backend MVP already supports the full personal-user loop:

1. Create a debate session.
2. Run 3 debate rounds with SSE streaming.
3. Trigger evaluation after round 3.

Current status:

- `POST /api/debate/start` is available.
- `POST /api/debate/stream` is available.
- `POST /api/debate/evaluate` is available.
- SQLite migration is ready through Alembic.
- Automated tests cover `start`, `stream`, `evaluate`, and `prompt_builder`.

## Local Start

1. Install dependencies.

```powershell
python -m pip install Flask Flask-SQLAlchemy SQLAlchemy alembic pytest requests python-dotenv
```

2. Initialize the SQLite database.

```powershell
python -m alembic -c alembic.ini upgrade head
```

3. Start Flask.

```powershell
python run.py
```

4. Health check.

```powershell
curl.exe http://127.0.0.1:5000/health
```

## Environment Variables

See [.env.example](/d:/dev/web/ai-debate-coach/.env.example).

Important fields:

- `DATABASE_URL`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_MODEL`
- `MAX_DEBATE_ROUNDS`
- `PROMPT_HISTORY_LIMIT`

Default local database:

```text
sqlite:///storage/debate_coach.db
```

## API Contract

Base URL:

```text
http://127.0.0.1:5000
```

### 1. Create Session

`POST /api/debate/start`

Request JSON:

```json
{
  "topic": "Should AI-assisted learning be widely adopted in universities?",
  "position": "正方"
}
```

Rules:

- `topic`: non-empty string, max length 100
- `position`: must be `正方` or `反方`

Response `201`:

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0",
  "topic": "Should AI-assisted learning be widely adopted in universities?",
  "position": "正方",
  "current_round": 0,
  "status": "created"
}
```

### 2. Stream Debate Reply

`POST /api/debate/stream`

Request JSON:

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0",
  "content": "AI can tailor pace and feedback to each student."
}
```

Response type:

```text
text/event-stream
```

SSE event types:

- `chunk`: partial assistant reply
- `done`: round finished
- `error`: current round failed

Example stream:

```text
event: chunk
data: {"session_id":"2896134b-0812-4cae-8188-c74896ca35b0","round_no":1,"content":"First part"}

event: chunk
data: {"session_id":"2896134b-0812-4cae-8188-c74896ca35b0","round_no":1,"content":"Second part"}

event: done
data: {"session_id":"2896134b-0812-4cae-8188-c74896ca35b0","round_no":1,"current_round":1,"is_final_round":false}
```

### 3. Evaluate Debate

`POST /api/debate/evaluate`

Request JSON:

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0"
}
```

Response `200`:

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0",
  "logic_score": 7,
  "evidence_score": 6,
  "fluency_score": 7,
  "suggestion": "Your stance is clear, but the evidence is still thin.",
  "fallback_used": false,
  "cached": false
}
```

## Frontend JS Example

The backend uses `fetch` for JSON APIs and streamed `fetch` for SSE-like reading.

### Create session

```js
export async function startDebate(baseUrl, topic, position) {
  const response = await fetch(`${baseUrl}/api/debate/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ topic, position }),
  });

  if (!response.ok) {
    throw await response.json();
  }

  return response.json();
}
```

### Read streamed debate response

```js
export async function streamDebateRound({
  baseUrl,
  sessionId,
  content,
  onChunk,
  onDone,
  onError,
}) {
  const response = await fetch(`${baseUrl}/api/debate/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      content,
    }),
  });

  if (!response.ok || !response.body) {
    const error = await response.json().catch(() => null);
    throw error || new Error("stream request failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const rawEvent of events) {
      const lines = rawEvent.split("\n");
      const eventLine = lines.find((line) => line.startsWith("event: "));
      const dataLine = lines.find((line) => line.startsWith("data: "));

      if (!eventLine || !dataLine) continue;

      const eventName = eventLine.replace("event: ", "").trim();
      const payload = JSON.parse(dataLine.replace("data: ", ""));

      if (eventName === "chunk") onChunk?.(payload);
      if (eventName === "done") onDone?.(payload);
      if (eventName === "error") onError?.(payload);
    }
  }
}
```

### Evaluate after round 3

```js
export async function evaluateDebate(baseUrl, sessionId) {
  const response = await fetch(`${baseUrl}/api/debate/evaluate`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ session_id: sessionId }),
  });

  if (!response.ok) {
    throw await response.json();
  }

  return response.json();
}
```

### Suggested page flow

```js
const session = await startDebate(baseUrl, topic, "正方");

await streamDebateRound({
  baseUrl,
  sessionId: session.session_id,
  content: userInput,
  onChunk(payload) {
    appendAssistantText(payload.content);
  },
  async onDone(payload) {
    if (payload.is_final_round) {
      const report = await evaluateDebate(baseUrl, session.session_id);
      renderEvaluation(report);
    } else {
      unlockInput();
    }
  },
  onError(payload) {
    showRetry(payload.message);
  },
});
```

## Error Format

All non-stream errors use JSON:

```json
{
  "error": {
    "code": "validation_error",
    "message": "position 只允许为“正方”或“反方”。",
    "details": null
  }
}
```

Common error codes:

- `validation_error`
- `not_found`
- `conflict`
- `llm_upstream_error`
- `internal_server_error`

## Manual End-to-End Script

### Step 1. Start a session

```powershell
@'
import json, urllib.request
url = "http://127.0.0.1:5000/api/debate/start"
payload = json.dumps({
    "topic": "Should AI-assisted learning be widely adopted in universities?",
    "position": "\u6b63\u65b9"
}, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=10) as resp:
    print(resp.read().decode("utf-8"))
'@ | python -
```

### Step 2. Stream 3 rounds and then evaluate

Replace the session id first.

```powershell
@'
import json
import requests

base = "http://127.0.0.1:5000"
session_id = "REPLACE_ME"
rounds = [
    "AI can tailor pace and feedback to each student.",
    "Teachers can use AI to find weak points faster.",
    "With clear review rules, AI can improve access to learning."
]

for idx, content in enumerate(rounds, start=1):
    response = requests.post(
        f"{base}/api/debate/stream",
        json={"session_id": session_id, "content": content},
        stream=True,
        timeout=20,
    )
    print(f"ROUND {idx} STATUS {response.status_code}")
    for line in response.iter_lines(decode_unicode=True):
        if line:
            print(line)
    print("---")

evaluation = requests.post(
    f"{base}/api/debate/evaluate",
    json={"session_id": session_id},
    timeout=20,
)
print(json.dumps(evaluation.json(), ensure_ascii=False, indent=2))
'@ | python -
```

## Test Commands

Run all tests:

```powershell
python -m pytest tests -q
```

Run stream tests only:

```powershell
python -m pytest tests/test_stream_api.py -q
```
