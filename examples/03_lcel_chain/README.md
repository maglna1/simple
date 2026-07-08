# 示例 03：LCEL（LangChain Expression Language）

LCEL 是 LangChain 推荐的现代写法：用 `|` 操作符把多个 `Runnable` 组件串成一条链。

## 运行

```bash
python examples/03_lcel_chain/main.py
```

## Runnable 协议

所有可以"接收输入、产生输出"的组件都实现了 `Runnable` 接口，可以用 `|` 连接：

```
┌──────────┐     ┌────────┐     ┌──────────┐     ┌────────┐
│  Prompt  │ ──▶ │  LLM   │ ──▶ │  Parser  │ ──▶ │ 输出   │
└──────────┘     └────────┘     └──────────┘     └────────┘
   字典           AIMessage        AIMessage        str
```

每个组件的输入 / 输出类型必须兼容：`Prompt` 输出 dict → `LLM` 输入 dict / 消息列表 → `Parser` 输入 `AIMessage`。

## 为什么用 LCEL

| 旧写法（LLMChain） | 新写法（LCEL） |
|---|---|
| 需要继承 / 实例化 Chain 类 | 任意 `Runnable` 直接 `\|` |
| 流式需要单独实现 `stream` 方法 | 任何链自动支持 `.stream()` |
| 异步需要单独实现 `ainvoke` | 自动支持 `.ainvoke()` / `.astream()` |
| 配置（callbacks、tags）需要单独管理 | 统一通过 `.with_config()` 注入 |

## 三个演示

### 演示 1：基本三段式

```python
chain = prompt | llm | StrOutputParser()
answer = chain.invoke({"question": "什么是 LangChain？"})
```

### 演示 2：多路分支

`RunnablePassthrough.assign(...)` 把同一份输入并行喂给多条子链，合并成 dict 输出。

```python
chain = RunnablePassthrough.assign(
    chinese=chinese_chain,
    english=english_chain,
)
```

### 演示 3：链式流式

链本身就是一个 Runnable，可以直接 `.stream()` 拿到增量输出。

## 期望输出

每个演示都会打印模型回复。具体文本因模型而异。

## 下一步

继续学习 [`examples/04_output_parser`](../04_output_parser/README.md)：用 Pydantic 解析器把模型输出变成强类型对象。