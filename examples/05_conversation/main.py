"""示例 05：多轮对话。

演示手动维护消息历史完成多轮对话。
ChatModel 本身是无状态的——"记忆"完全由调用方维护的消息列表承担。

运行方式：
    python examples/05_conversation/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402

from utils.llm import get_chat_model  # noqa: E402


def demo_manual_history() -> None:
    """演示 1：手动维护消息列表。"""
    print("=" * 60)
    print("[演示 1] 手动维护消息历史")
    print("=" * 60)

    llm = get_chat_model()

    # 消息列表就是"对话历史"
    history: list = [
        SystemMessage(content="你是一位简洁的中文助手，回答不超过两句话。"),
    ]

    turns = [
        "你好，我叫小明。",
        "我叫什么名字？",
        "我刚才说我是谁？",
    ]

    for user_input in turns:
        # 把当前用户输入追加进历史
        history.append(HumanMessage(content=user_input))
        # 用完整历史调用模型
        response = llm.invoke(history)
        print(f"\n用户: {user_input}")
        print(f"助手: {response.content}")

        # 把模型回复也追加进历史，下一轮要用
        history.append(response)

    print(f"\n（对话结束后，消息历史共 {len(history)} 条）\n")


def demo_turn_counter() -> None:
    """演示 2：用回调统计每轮 token 消耗。"""
    print("=" * 60)
    print("[演示 2] 每轮 token 消耗统计")
    print("=" * 60)

    from langchain_core.callbacks import BaseCallbackHandler

    class TokenCounter(BaseCallbackHandler):
        """统计每个 LLM 调用的 token 消耗。"""

        def __init__(self) -> None:
            self.total_input = 0
            self.total_output = 0

        def on_llm_end(self, response, **kwargs) -> None:  # type: ignore[no-untyped-def]
            # response.generations[0][0].message.usage_metadata 在新版 langchain 中可用
            try:
                usage = response.generations[0][0].message.usage_metadata
                if usage:
                    self.total_input += usage.get("input_tokens", 0)
                    self.total_output += usage.get("output_tokens", 0)
            except (AttributeError, IndexError):
                pass

    counter = TokenCounter()
    llm = get_chat_model().with_config({"callbacks": [counter]})

    history: list = [
        SystemMessage(content="用一句话回答问题。"),
        HumanMessage(content="Python 是什么？"),
    ]
    response = llm.invoke(history)
    print(f"\n回复: {response.content}")
    print(f"累计 input tokens: {counter.total_input}")
    print(f"累计 output tokens: {counter.total_output}\n")


if __name__ == "__main__":
    demo_manual_history()
    demo_turn_counter()