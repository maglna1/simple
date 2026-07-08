"""示例 01：第一次对话。

演示 ChatModel 的两种调用方式：
    1. invoke：一次性拿到完整响应
    2. stream：逐 chunk 流式输出

运行方式（在仓库根目录）：
    python examples/01_hello_llm/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# 把仓库根目录加入 sys.path，使得 `from utils.xxx import ...` 可用。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.llm import get_chat_model  # noqa: E402


def demo_invoke() -> None:
    """演示 1：invoke 一次性调用。"""
    print("=" * 60)
    print("[演示 1] invoke：一次性拿到完整响应")
    print("=" * 60)

    llm = get_chat_model()
    response = llm.invoke("用一句话介绍 LangChain。")

    print(f"\n模型回复：\n{response.content}\n")

    # AIMessage 上的元信息
    print("元信息：")
    print(f"  - 类型: {type(response).__name__}")
    print(f"  - 响应 ID: {response.id}")
    print(f"  - 用量: {response.usage_metadata}")
    print()


def demo_stream() -> None:
    """演示 2：stream 流式输出。"""
    print("=" * 60)
    print("[演示 2] stream：逐 chunk 流式输出")
    print("=" * 60)

    llm = get_chat_model()
    print("\n模型回复（流式）：")
    print("  ", end="", flush=True)
    for chunk in llm.stream("用一句话介绍 LangChain。"):
        # chunk.content 可能是空字符串（首尾 chunk 不一定有文本）
        print(chunk.content, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    demo_invoke()
    demo_stream()