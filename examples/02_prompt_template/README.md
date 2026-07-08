# 示例 02：Prompt 模板

Prompt 模板把"用户输入"与"提示词结构"分离，让提示词可以参数化、复用、版本化。

## 运行

```bash
python examples/02_prompt_template/main.py
```

## 三种模板

### 1. `PromptTemplate.from_template` —— 字符串模板

最简单的模板，只生成一段纯文本：

```python
template = PromptTemplate.from_template("请把下面这句话翻译成{language}：{sentence}")
template.format(language="法语", sentence="今天天气真好")
```

适用：纯文本任务（不涉及消息角色）。

### 2. `ChatPromptTemplate.from_messages` —— 多角色消息模板

为聊天模型设计，每条消息有自己的角色：

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位{role}，回答要{style}。"),
    ("human", "{question}"),
])
messages = prompt.format_messages(role="诗人", style="简洁", question="春天")
```

元组写法 `("role", "text")` 是简写，等价于显式构造 `SystemMessage(...)` / `HumanMessage(...)`。

适用：所有聊天模型调用。**推荐作为默认选择。**

### 3. Few-shot Prompt

通过给出"输入-输出"示例对，引导模型按指定格式 / 风格回答：

```python
FewShotPromptTemplate(
    examples=[{"word": "开心", "antonym": "难过"}, ...],
    example_prompt=PromptTemplate.from_template("词: {word}\n反义词: {antonym}"),
    prefix="给出下面词语的反义词：",
    suffix="词: {word}\n反义词:",
    input_variables=["word"],
)
```

适用：需要约束输出格式 / 风格时。

> **进阶**：可以用 `ChatPromptTemplate.from_messages` 直接拼装 Few-shot，把示例作为 `human`/`assistant` 交替消息，效果往往比字符串 Few-shot 更好。

## 消息角色

| 角色 | 含义 | 何时用 |
|---|---|---|
| `system` | 系统提示词 | 设定模型行为 / 人格 / 约束 |
| `human` | 用户输入 | 用户的真实问题 |
| `ai` | 模型回复（用于历史） | 多轮对话（见 `examples/05`） |
| `tool` | 工具调用结果 | Agent（见 `examples/08`） |

## 期望输出

每个演示会先打印渲染后的 Prompt 字符串（或消息列表），再打印模型回复。

## 下一步

继续学习 [`examples/03_lcel_chain`](../03_lcel_chain/README.md)：用 `|` 把 prompt / llm / parser 串成一条链。