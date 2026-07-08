# 示例 05：多轮对话

ChatModel 本身是**无状态**的。"对话"靠调用方维护的消息列表实现。

## 运行

```bash
python examples/05_conversation/main.py
```

## 核心思想

```python
history = [SystemMessage(content="你是助手。")]
history.append(HumanMessage(content="第一轮问题"))
response = llm.invoke(history)
history.append(response)  # 把 AI 回复也塞进历史
# 下一轮
history.append(HumanMessage(content="第二轮问题"))
response = llm.invoke(history)
```

每次调用都要把"完整历史"传给模型。这有两个副作用：

1. **成本线性增长**：每轮都把所有历史重新发一遍，token 消耗随轮次线性累积。
2. **有上下文窗口上限**：超过模型 max_tokens 会报错。

## 手动 vs ConversationChain

| 方案 | 优点 | 缺点 |
|---|---|---|
| 手动维护消息列表（**推荐**） | 完全可控；适配任何链式调用 | 需要自己处理裁剪、持久化 |
| LangChain 内置 `ConversationChain` | 一行搞定 | 黑盒、难定制、在新版 LangChain 中已被 LCEL 取代 |

LangChain 0.3 起官方推荐**手动 + LCEL**，本示例采用这种方式。

## Token 统计（演示 2）

通过 `BaseCallbackHandler` 子类，可以在每次 LLM 调用结束时拿到 usage 信息：

```python
class TokenCounter(BaseCallbackHandler):
    def on_llm_end(self, response, **kwargs):
        usage = response.generations[0][0].message.usage_metadata
        ...
```

挂在模型上：

```python
llm = get_chat_model().with_config({"callbacks": [TokenCounter()]})
```

`with_config(...)` 把 callbacks 注入到该次调用，不影响其他示例。

## 长对话策略

超过上下文窗口时：

- **滑动窗口**：只保留最近 N 轮
- **摘要压缩**：让模型把早期对话总结成一段文字塞进 system message
- **外部存储**：把对话存数据库，每次只取相关的几段拼到 prompt 里

这些都属于工程化话题，本合集不展开。

## 期望输出

```
用户: 你好，我叫小明。
助手: 你好小明，很高兴认识你。

用户: 我叫什么名字？
助手: 你叫小明。

用户: 我刚才说我是谁？
助手: 你刚才说你叫小明。
```

## 下一步

继续学习 [`examples/06_rag_basics`](../06_rag_basics/README.md)：检索增强生成（RAG）入门。