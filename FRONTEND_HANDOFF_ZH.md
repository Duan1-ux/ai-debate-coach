# 前端对接说明

当前后端已经完成个人用户 MVP 主链路：

1. 创建辩论会话
2. 进行 3 回合流式辩论
3. 第 3 回合后生成评分报告

当前可用接口：

- `POST /api/debate/start`
- `POST /api/debate/stream`
- `POST /api/debate/evaluate`

## 当前文档和前一版文档的区别

前面那份英文文档不是重复工作，它主要解决两个问题：

- 后端接口契约是什么
- 手工怎么把整条链路跑通

这次新增内容解决另外两个问题：

- 前端页面里具体怎么写 `fetch` 和流式读取代码
- 给组内传阅时，字段和状态含义如何用中文快速说明

## 一、接口字段中文说明

### 1. 创建会话

接口：

```text
POST /api/debate/start
```

请求体：

```json
{
  "topic": "大学教育是否应该全面推行 AI 辅助学习",
  "position": "正方"
}
```

字段说明：

- `topic`：辩题，不能为空，最大 100 个字符
- `position`：用户持方，只允许 `正方` 或 `反方`

返回体：

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0",
  "topic": "大学教育是否应该全面推行 AI 辅助学习",
  "position": "正方",
  "current_round": 0,
  "status": "created"
}
```

返回字段说明：

- `session_id`：本次辩论的唯一会话 ID，后续所有请求都要带它
- `current_round`：当前已完成回合数，创建后是 `0`
- `status`：当前会话状态，初始为 `created`

### 2. 流式辩论

接口：

```text
POST /api/debate/stream
```

请求体：

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0",
  "content": "我方认为 AI 辅助学习可以提升个性化教学效率。"
}
```

字段说明：

- `session_id`：会话 ID
- `content`：用户本回合发言内容

返回类型：

```text
text/event-stream
```

服务端会持续推送三种事件：

- `chunk`：AI 当前输出的一小段文本
- `done`：这一回合正式结束
- `error`：本回合流式生成失败

`chunk` 示例：

```text
event: chunk
data: {"session_id":"...","round_no":1,"content":"第一段文本"}
```

字段说明：

- `round_no`：当前是第几回合
- `content`：本次追加到 AI 气泡中的文本片段

`done` 示例：

```text
event: done
data: {"session_id":"...","round_no":1,"current_round":1,"is_final_round":false}
```

字段说明：

- `current_round`：后端已经确认写入成功的回合数
- `is_final_round`：是否已完成第 3 回合

`error` 示例：

```text
event: error
data: {"session_id":"...","round_no":2,"message":"流式生成失败，请重试当前回合。"}
```

字段说明：

- `message`：前端直接展示给用户的错误提示

### 3. 评分报告

接口：

```text
POST /api/debate/evaluate
```

请求体：

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0"
}
```

返回体：

```json
{
  "session_id": "2896134b-0812-4cae-8188-c74896ca35b0",
  "logic_score": 7,
  "evidence_score": 6,
  "fluency_score": 7,
  "suggestion": "你的立场表达清楚，但论据还不够扎实。",
  "fallback_used": false,
  "cached": false
}
```

字段说明：

- `logic_score`：逻辑严密性，0 到 10
- `evidence_score`：论据充实度，0 到 10
- `fluency_score`：表达流畅性，0 到 10
- `suggestion`：给用户展示的文字建议
- `fallback_used`：是否触发了解析降级
- `cached`：是否直接返回之前已经生成过的评分

## 二、前端页面接入建议

建议前端按这个时机调用：

1. 设置页点击开始
2. 调 `/api/debate/start`
3. 保存 `session_id`
4. 跳转到辩论页
5. 每次用户发送发言时调 `/api/debate/stream`
6. 边收 `chunk` 边更新 AI 回复气泡
7. 收到 `done` 后解锁输入框
8. 如果 `is_final_round === true`，立刻调 `/api/debate/evaluate`
9. 渲染评分页

## 三、前端可直接复制的 JS 示例

### 1. 创建会话

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

### 2. 流式读取 AI 回复

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

### 3. 请求评分报告

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

### 4. 一个完整调用示例

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

## 四、错误响应说明

非流式错误统一返回：

```json
{
  "error": {
    "code": "validation_error",
    "message": "position 只允许为“正方”或“反方”。",
    "details": null
  }
}
```

常见错误码：

- `validation_error`：参数不合法
- `not_found`：会话不存在
- `conflict`：流程冲突，比如第 4 回合继续发送
- `llm_upstream_error`：上游模型调用失败
- `internal_server_error`：服务内部异常

## 五、建议前端重点注意的坑

- `/api/debate/stream` 不是普通 JSON 接口，必须按流读取
- 同一个回合要把多个 `chunk` 拼到一个 AI 消息气泡里
- 只有收到 `done` 才能认为这一回合真正完成
- 第 3 回合结束不是让用户自己点评分，而是前端自动调 `/api/debate/evaluate`
- 如果直接用某些 Windows 终端手发中文 JSON，可能碰到编码问题；前端浏览器 `fetch` 正常发送 UTF-8 就没有这个问题
