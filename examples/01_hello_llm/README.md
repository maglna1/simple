# 示例 01：第一次对话

演示 ChatModel 的两种调用方式：`invoke` 与 `stream`。

## 运行

在仓库根目录执行：

```bash
python examples/01_hello_llm/main.py
```

## 关键概念

### ChatModel

`ChatModel` 是 LangChain 中与"对话模型"打交道的统一接口（`BaseChatModel`）。它接收一组 `BaseMessage`（`HumanMessage` / `AIMessage` / `SystemMessage` / `ToolMessage`），返回 `AIMessage`。

我们通过 `utils.llm.get_chat_model()` 获取实例，**不直接构造 `ChatOpenAI`**——因为：

1. 凭据统一在 `utils/llm.py` 里管理。
2. 切换模型 / 改 `base_url` 只需要改一处。
3. 测试时可以替换为 mock。

### invoke：一次性调用

```python
response = llm.invoke("用一句话介绍 LangChain。")
print(response.content)        # 文本内容
print(response.usage_metadata) # token 用量
```

返回一个完整的 `AIMessage`。简单场景够用，但响应是阻塞的——用户必须等模型生成完所有 token 后才能看到第一个字。

### stream：流式输出

```python
for chunk in llm.stream("用一句话介绍 LangChain。"):
    print(chunk.content, end="", flush=True)
```

逐 chunk 返回，首字延迟显著降低，适合长文本生成 / 聊天 UI。`chunk` 也是 `AIMessageChunk` 类型，但只有当前 chunk 包含的增量内容。

## invoke vs stream 何时用

| 场景 | 推荐 |
|---|---|
| 短回复、批处理、脚本里一次性调用 | `invoke` |
| 长回复、聊天 UI、需要首字延迟低 | `stream` |
| 异步上下文（FastAPI / WebSocket） | `ainvoke` / `astream`（见 `examples/10`） |

## 期望输出

```
============================================================
[演示 1] invoke：一次性拿到完整响应
============================================================

模型回复：
LangChain 是一个用于构建大语言模型应用的开发框架。

元信息：
  - 类型: AIMessage
  - 响应 ID: ...
  - 用量: {'input_tokens': ..., 'output_tokens': ..., 'total_tokens': ...}

============================================================
[演示 2] stream：逐 chunk 流式输出
============================================================

模型回复（流式）：
  LangChain 是一个用于构建大语言模型应用的开发框架。
```

> 实际文本由模型生成，可能与示例不同。

## 已知限制

- MiniMax-M3 对 `stream` 的支持需要在首次运行时确认。如果模型不支持流式，`stream()` 会一次性返回完整响应（与 `invoke` 行为相同）。本示例的实际表现会写回到本 README 的"已知限制"小节。

## 下一步

继续学习 [`examples/02_prompt_template`](../02_prompt_template/README.md)：用 Prompt 模板把"用户输入"和"提示词结构"分离。