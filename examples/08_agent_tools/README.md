# 示例 08：Agent 与自定义工具

Agent 让模型在回答前**主动调用工具**（calculator、搜索、数据库查询…），再根据工具结果生成最终回复。

## 运行

```bash
python examples/08_agent_tools/main.py
```

## 自定义工具

用 `@tool` 装饰器：

```python
@tool
def calculator(expression: str) -> str:
    """计算一个简单的数学表达式。"""
    return str(eval(expression))
```

**关键点**：

1. **docstring 就是工具的"说明书"**——模型根据 docstring 决定何时调、传什么参数。
2. **类型注解**决定参数 schema。LangChain 用 Pydantic 自动生成 JSON schema。
3. **返回字符串**——工具结果最终会被喂回模型。

## 把工具绑定到 LLM

```python
llm_with_tools = llm.bind_tools([calculator, get_word_count])
```

`bind_tools` 在每次调用时给模型"看到"工具清单。模型可以输出 `tool_calls` 字段表示"我要调这个工具"。

## ReAct 循环

```
模型思考 ──▶ 决定调用工具 ──▶ 执行工具 ──▶ 把结果喂回模型 ──▶ 模型再思考 ──▶ ... ──▶ 最终回复
```

新版 LangChain 把这个循环交给 **LangGraph** 实现（`create_react_agent`），状态图自动维护"消息列表"作为唯一状态。

```python
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(llm_with_tools, tools)
result = agent_executor.invoke({"messages": [HumanMessage(content="...")]})
```

返回 `result["messages"]` 是完整的对话轨迹。

## 已知限制

- **依赖模型的 native tool calling 支持**：MiniMax-M3 是否原生支持 `tool_calls` 字段需要在首次运行时验证。如果模型不支持，本示例会失败，提示会写回本 README 的"已知限制"小节。
- **fallback 方案**：若 MiniMax-M3 不支持 tool calling，可以改用 LangChain 较旧的 `create_react_agent`（来自 `langchain.agents`）+ 一个能输出特定格式提示词的模型，或者切换到支持 tool calling 的模型。
- **`eval` 的安全风险**：本示例用 `eval` 计算数学表达式仅作演示。生产环境应使用 `asteval`、`simpleeval` 等沙箱。

## 下一步

继续学习 [`examples/09_langgraph`](../09_langgraph/README.md)：自己定义状态图，更灵活地控制 Agent 行为。