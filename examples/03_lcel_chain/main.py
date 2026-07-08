"""示例 03：LCEL（LangChain Expression Language）。

用 `|` 操作符把多个 Runnable 组件串成一条链：
    prompt | llm | output_parser

运行方式：
    python examples/03_lcel_chain/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.runnables import RunnablePassthrough  # noqa: E402
from utils.llm import get_chat_model  # noqa: E402


def demo_basic_chain() -> None:
    """演示 1：prompt | llm | parser —— 最经典的 LCEL 三段式。"""
    print("=" * 60)
    print("[演示 1] prompt | llm | StrOutputParser")
    print("=" * 60)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一位幽默的中文助手，喜欢用一句话回答。"),
            ("human", "{question}"),
        ]
    )
    llm = get_chat_model()
    parser = StrOutputParser()

    # 用 | 串起来：每一步的输出作为下一步的输入
    chain = prompt | llm | parser

    # 最终 invoke 时只需要传入 prompt 模板里声明的变量
    answer = chain.invoke({"question": "什么是 LangChain？"})
    print(f"\n模型回复（一行）：\n  {answer}\n")


def demo_parallel_branches() -> None:
    """演示 2：用 RunnablePassthrough 与字典组合实现"同一输入，多路处理"。

    经典场景：让模型同时给"中文回答"和"英文翻译"。
    """
    print("=" * 60)
    print("[演示 2] 多路分支：同一问题，多角度回答")
    print("=" * 60)

    llm = get_chat_model()

    # 子链 1：中文回答
    chinese_chain = (
        ChatPromptTemplate.from_template("用中文一句话回答：{question}")
        | llm
        | StrOutputParser()
    )
    # 子链 2：英文回答
    english_chain = (
        ChatPromptTemplate.from_template("Answer in one English sentence: {question}")
        | llm
        | StrOutputParser()
    )

    # 组合：把同一个 question 同时送进两条链
    chain = RunnablePassthrough.assign(
        chinese=chinese_chain,
        english=english_chain,
    )

    result = chain.invoke({"question": "为什么天空是蓝色的？"})
    print("\n结果字典：")
    for k, v in result.items():
        print(f"  - {k}: {v}")
    print()


def demo_stream_chain() -> None:
    """演示 3：链本身也可以流式输出。"""
    print("=" * 60)
    print("[演示 3] chain.stream() —— 链式流式")
    print("=" * 60)

    chain = (
        ChatPromptTemplate.from_template("用三句话介绍{topic}。")
        | get_chat_model()
        | StrOutputParser()
    )

    print("\n模型回复（流式）：")
    print("  ", end="", flush=True)
    for chunk in chain.stream({"topic": "Python 装饰器"}):
        print(chunk, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    demo_basic_chain()
    demo_parallel_branches()
    demo_stream_chain()