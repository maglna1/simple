"""示例 02：Prompt 模板。

演示 LangChain 中三种常见的 Prompt 模板：
    1. PromptTemplate.from_template —— 简单字符串模板
    2. ChatPromptTemplate.from_messages —— 多角色消息模板
    3. Few-shot 模板 —— 通过消息列表给出多个示例

运行方式（在仓库根目录）：
    python examples/02_prompt_template/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, FewShotPromptTemplate  # noqa: E402
from utils.llm import get_chat_model  # noqa: E402


def demo_simple_template() -> None:
    """演示 1：PromptTemplate.from_template —— 简单字符串模板。"""
    print("=" * 60)
    print("[演示 1] PromptTemplate.from_template")
    print("=" * 60)

    template = PromptTemplate.from_template(
        "请把下面这句话翻译成{language}：{sentence}"
    )
    # 模板渲染（不调用模型）
    rendered = template.format(language="法语", sentence="今天天气真好")
    print(f"\n渲染后的 Prompt:\n  {rendered}\n")

    # 完整流程：format 后再调用
    llm = get_chat_model()
    # 也可以直接 invoke_template / llm.invoke(template.format(...))
    formatted = template.format(language="法语", sentence="今天天气真好")
    response = llm.invoke(formatted)
    print(f"模型回复：\n  {response.content}\n")


def demo_chat_template() -> None:
    """演示 2：ChatPromptTemplate.from_messages —— 多角色消息模板。"""
    print("=" * 60)
    print("[演示 2] ChatPromptTemplate.from_messages")
    print("=" * 60)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一位{role}，回答要{style}。"),
            ("human", "{question}"),
        ]
    )

    messages = prompt.format_messages(
        role="诗人",
        style="简洁、富有意象",
        question="春天",
    )

    print("\n渲染后的消息列表:")
    for msg in messages:
        print(f"  - [{type(msg).__name__}] {msg.content}")
    print()

    llm = get_chat_model()
    response = llm.invoke(messages)
    print(f"模型回复：\n  {response.content}\n")


def demo_few_shot() -> None:
    """演示 3：Few-shot 模板 —— 通过示例引导模型输出风格。"""
    print("=" * 60)
    print("[演示 3] Few-shot Prompt")
    print("=" * 60)

    examples = [
        {"word": "开心", "antonym": "难过"},
        {"word": "高大", "antonym": "矮小"},
    ]

    example_prompt = PromptTemplate.from_template("词: {word}\n反义词: {antonym}")

    few_shot = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix="给出下面词语的反义词：",
        suffix="词: {word}\n反义词:",
        input_variables=["word"],
    )

    rendered = few_shot.format(word="温暖")
    print(f"\n渲染后的 Prompt:\n{rendered}\n")

    llm = get_chat_model()
    response = llm.invoke(rendered)
    print(f"模型回复：\n  {response.content}\n")


if __name__ == "__main__":
    demo_simple_template()
    demo_chat_template()
    demo_few_shot()