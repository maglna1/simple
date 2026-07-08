"""示例 04：输出解析器。

演示两种结构化输出：
    1. JsonOutputParser —— 解析为 Python dict
    2. PydanticOutputParser —— 解析为 Pydantic 模型（强类型、可校验）

运行方式：
    python examples/04_output_parser/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from utils.llm import get_chat_model  # noqa: E402


# ============ 演示 1：JsonOutputParser ============
def demo_json_parser() -> None:
    """演示 1：用 JsonOutputParser 把模型输出解析为 dict。"""
    print("=" * 60)
    print("[演示 1] JsonOutputParser → dict")
    print("=" * 60)

    parser = JsonOutputParser()
    # 让 parser 自动把"输出格式说明"注入到 prompt 里
    format_instructions = parser.get_format_instructions()
    print(f"\n格式说明（前 120 字）：\n  {format_instructions[:120]}...\n")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一位严谨的数据提取助手。\n{format_instructions}"),
            ("human", "从下面文本提取人物信息：\n{text}"),
        ]
    )

    chain = prompt.partial(format_instructions=format_instructions) | get_chat_model() | parser

    result = chain.invoke(
        {
            "text": "爱因斯坦于 1879 年出生在德国乌尔姆，是 20 世纪最伟大的物理学家之一。"
        }
    )
    print("解析结果（dict）：")
    for k, v in result.items():
        print(f"  - {k}: {v}")
    print(f"  类型: {type(result).__name__}\n")


# ============ 演示 2：PydanticOutputParser ============
class Person(BaseModel):
    """人物信息结构化模型。"""

    name: str = Field(description="人物姓名")
    birth_year: int = Field(description="出生年份")
    nationality: str = Field(description="国籍")
    profession: str = Field(description="职业")


def demo_pydantic_parser() -> None:
    """演示 2：用 PydanticOutputParser 解析为 Pydantic 模型。"""
    print("=" * 60)
    print("[演示 2] PydanticOutputParser → Pydantic 模型")
    print("=" * 60)

    parser = PydanticOutputParser(pydantic_object=Person)
    format_instructions = parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一位严谨的数据提取助手。\n{format_instructions}"),
            ("human", "从下面文本提取人物信息：\n{text}"),
        ]
    )

    chain = prompt.partial(format_instructions=format_instructions) | get_chat_model() | parser

    result = chain.invoke(
        {"text": "钱学森于 1911 年出生在中国杭州，是著名物理学家与航天之父。"}
    )
    print(f"\n解析结果（{type(result).__name__} 实例）：")
    print(f"  - name: {result.name}")
    print(f"  - birth_year: {result.birth_year}")
    print(f"  - nationality: {result.nationality}")
    print(f"  - profession: {result.profession}")
    # Pydantic 模型自带校验：访问 result.dict() 得到 dict，访问 result.json() 得到 JSON 字符串
    print(f"  转 dict: {result.model_dump()}")
    print()


if __name__ == "__main__":
    demo_json_parser()
    demo_pydantic_parser()