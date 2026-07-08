"""示例 08：Agent 与自定义工具。

演示：
    1. 用 @tool 装饰器定义本地工具
    2. 把工具绑定到 LLM
    3. 构造一个简单的 Agent 循环：模型决定调工具 → 执行工具 → 把结果喂回模型 → 决定下一步

注意：
    LangChain 0.3 起 `create_react_agent` 已被移到 `langgraph.prebuilt`。
    本示例用 LangGraph 实现 Agent（也是当前官方推荐路径）。

运行方式：
    python examples/08_agent_tools/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain.agents import create_agent  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402

from utils.llm import get_chat_model  # noqa: E402


# ============ 自定义工具 ============
@tool
def calculator(expression: str) -> str:
    """计算一个简单的数学表达式，例如 '2 + 3 * 4'。

    Args:
        expression: 合法的 Python 数学表达式

    Returns:
        计算结果的字符串表示
    """
    # 注意：实际生产中 eval 很危险，这里仅作示例
    try:
        result = eval(expression)  # noqa: S307
        return str(result)
    except Exception as e:  # noqa: BLE001
        return f"计算错误: {e}"


@tool
def get_word_count(text: str) -> str:
    """统计一段文本的字符数（不含空格）和词数（粗略按空格分）。

    Args:
        text: 要统计的文本

    Returns:
        形如 "字符数: X, 词数: Y" 的字符串
    """
    chars_no_space = len(text.replace(" ", ""))
    words = len(text.split())
    return f"字符数(不含空格): {chars_no_space}, 词数: {words}"


def main() -> None:
    print("=" * 60)
    print("[Agent] 自定义工具 + ReAct")
    print("=" * 60)

    llm = get_chat_model()
    tools = [calculator, get_word_count]
    # 把工具绑定到 LLM：模型可以选择调用工具
    llm_with_tools = llm.bind_tools(tools)

    # 用 LangChain 1.0 的预构建 Agent（LangGraph 1.0 已把这函数搬到 langchain.agents）
    agent_executor = create_agent(llm_with_tools, tools)

    questions = [
        "计算 (15 + 27) * 3 - 10 的结果",
        "统计这段文本的词数和字符数：'LangChain 是一个用于构建大语言模型应用的开发框架'",
    ]

    for q in questions:
        print(f"\n用户: {q}")
        # Agent 自动决定：要不要调用工具、调哪个、参数是什么
        result = agent_executor.invoke({"messages": [HumanMessage(content=q)]})

        # result["messages"] 包含完整的思考-工具调用-最终回复
        print("Agent 内部轨迹：")
        for msg in result["messages"]:
            tag = type(msg).__name__
            content_preview = (msg.content or "")[:80] if isinstance(msg.content, str) else "<non-text>"
            print(f"  - [{tag}] {content_preview}")
            # ToolMessage 还会带 tool_call_id
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    print(f"    ↳ 调工具: {tc['name']}({tc['args']})")

        # 最后一条 AIMessage 是最终回复
        final = result["messages"][-1]
        print(f"\n最终回复: {final.content}\n")


if __name__ == "__main__":
    main()