# 示例 09：LangGraph —— 状态化工作流

LangGraph 让"用图的方式思考 Agent / 工作流"。本示例构造最简单的两节点图：`retrieve → generate`。

## 运行

```bash
# 首次运行需要先有 Chroma 索引（examples/07 已经创建过）
# 若还没创建，先跑一次：python examples/07_rag_vectorstore/main.py
python examples/09_langgraph/main.py
```

> 本示例依赖 `examples/07_rag_vectorstore/chroma` 下的索引。先跑示例 07 建好索引。

## 心智模型

```
┌─────┐    ┌─────────┐    ┌─────────┐    ┌─────┐
│START│ ─▶ │ retrieve│ ─▶ │ generate│ ─▶ │ END │
└─────┘    └─────────┘    └─────────┘    └─────┘
              节点 1          节点 2
```

每个节点是一个函数：

```python
def retrieve_node(state: RAGState) -> dict:
    docs = vectorstore.similarity_search(state["question"])
    return {"documents": [...]}
```

节点接收**完整 State**，返回**部分字段更新**。LangGraph 自动合并更新到 State。

## State 定义

```python
class RAGState(TypedDict):
    question: str
    documents: list[str]
    answer: str
```

State 是 TypedDict，节点返回 `dict` 即可增量更新字段。

## 持久化（MemorySaver）

```python
from langgraph.checkpoint.memory import MemorySaver

app = workflow.compile(checkpointer=MemorySaver())
app.invoke({"question": "..."}, config={"configurable": {"thread_id": "demo"}})
```

`MemorySaver` 把每次 invoke 的完整 State 快照存到内存里。下次 invoke 用相同 `thread_id` 即可拿到前一次的状态。

> 跨进程 / 跨重启：用 `SqliteSaver` 或 `PostgresSaver`。

## 为什么用 LangGraph 而不是直接 LCEL

| 场景 | 选 LCEL | 选 LangGraph |
|---|---|---|
| 单步推理（prompt → llm → parser） | ✓ | |
| 线性链（A → B → C） | ✓ | ✓ |
| **条件分支**（if X then A else B） | | ✓ |
| **循环**（agent 反复思考-行动） | | ✓ |
| **跨调用状态持久化** | | ✓（via checkpointer） |
| 人机协同（Human-in-the-loop） | | ✓ |

## 下一步

继续学习 [`examples/10_streaming_async`](../10_streaming_async/README.md)：流式 / 异步 / 回调。