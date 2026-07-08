# 示例 10：流式 / 异步 / 回调

三件 LangChain 生产场景必学的事放在一起。

## 运行

```bash
python examples/10_streaming_async/main.py
```

## 三件事

### 1. 同步流式：`llm.stream()`

```python
for chunk in llm.stream("..."):
    print(chunk.content, end="", flush=True)
```

逐 chunk 返回。适合 CLI / 终端场景。

### 2. 异步调用：`await llm.ainvoke()`

```python
response = await llm.ainvoke("...")
```

适合 FastAPI / WebSocket / 异步脚本。**Async 不是"为了快"，而是"为了不阻塞"**——一个请求在等 LLM 返回时，可以去服务别的请求。

### 3. 异步流式 + 并发：`astream` + `asyncio.gather`

```python
async def stream_one(q):
    return "".join([chunk async for chunk in llm.astream(q)])

answers = await asyncio.gather(*(stream_one(q) for q in questions))
```

三个问题并发跑，总耗时约等于最慢那一条（而不是三条之和）。

## 自定义回调

继承 `BaseCallbackHandler`，钩子在 LLM 生命周期触发：

| 钩子 | 何时触发 |
|---|---|
| `on_llm_start` | 调用开始 |
| `on_llm_new_token` | 每个新 token 到达（仅流式） |
| `on_llm_end` | 调用结束，能拿到 usage_metadata |

挂在模型上：

```python
metrics = MetricsCallback()
llm = get_chat_model().with_config({"callbacks": [metrics]})
```

## 同步 / 异步 / 流式 适用场景

| 场景 | 推荐 |
|---|---|
| CLI 脚本、单次调用 | `invoke` |
| 长文本生成、聊天 UI | `stream` |
| FastAPI / Web 服务 | `ainvoke` / `astream` |
| 批量独立问题 | `asyncio.gather` + `astream` |

## 期望输出

每个演示会打印模型回复和统计指标（首字延迟、总耗时、token 数）。

## 已知限制

- `on_llm_new_token` 仅在流式调用时触发，阻塞调用不会触发。
- 部分模型（包括 MiniMax-M3）对 `stream` 的实际支持需要在首次运行验证。如果不支持流式，本示例的演示 1/3 会退化为一次性输出。
- `BaseCallbackHandler` 的回调是同步执行的；如需异步钩子可继承 `AsyncBaseCallbackHandler`。

## 合集收尾

至此你已经走完 11 个示例，覆盖了 LangChain 的主要用法。回到 [顶层 README](../../README.md) 复习整体路径，或继续探索：

- [LangGraph 官方教程](https://langchain-ai.github.io/langgraph/tutorials/)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)