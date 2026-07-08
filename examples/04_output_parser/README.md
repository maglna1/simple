# 示例 04：输出解析器

把"模型自由文本"变成"程序可用的强类型对象"，是 LLM 应用的关键一步。

## 运行

```bash
python examples/04_output_parser/main.py
```

## 两种解析器

### `JsonOutputParser` → dict

最简单：模型按 JSON 输出，解析为 Python `dict`。

```python
parser = JsonOutputParser()
chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser
```

特点：灵活，无 schema 约束。

### `PydanticOutputParser` → Pydantic 模型

把模型输出解析为 Pydantic BaseModel 实例。

```python
class Person(BaseModel):
    name: str
    birth_year: int

parser = PydanticOutputParser(pydantic_object=Person)
chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser
result: Person = chain.invoke({"text": "..."})
print(result.birth_year)  # 类型安全
```

特点：
- 字段类型自动校验（int 拿不到时抛错）
- 自带 `model_dump()` / `model_dump_json()` 序列化方法
- `.get_format_instructions()` 会把 schema 自动生成给模型的提示注入 prompt

## `format_instructions` 的作用

`get_format_instructions()` 返回一段给模型看的"输出格式说明"，告诉模型**应该按什么结构输出**。把它通过 `prompt.partial(...)` 注入到 system 消息里：

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位助手。\n{format_instructions}"),
    ("human", "{text}"),
])
chain = prompt.partial(format_instructions=parser.get_format_instructions()) | llm | parser
```

`prompt.partial(...)` 会把 `format_instructions` 固定下来，`chain.invoke()` 时只需要传入剩下的变量（如 `text`）。

## 期望输出

每个演示会打印解析后的字段值和类型。

## 已知限制

- 小模型在 JSON / Pydantic 严格格式输出上失败率较高，必要时可降低 `temperature`（如 `get_chat_model(temperature=0.0)`）。
- 若模型不能稳定输出有效 JSON，可改用 LangChain 较新的 `with_structured_output(Person)` 接口（要求模型支持 tool calling / function calling，MiniMax-M3 是否支持需在 `examples/08` 验证）。

## 下一步

继续学习 [`examples/05_conversation`](../05_conversation/README.md)：手动维护多轮对话历史。