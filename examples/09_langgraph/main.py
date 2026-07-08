"""示例 09：LangGraph —— 状态化工作流。

用一个最简单的 RAG 工作流演示 LangGraph 的核心概念：
    1. StateGraph：定义节点 + 边
    2. 节点 (Node)：接收 State，返回 State 的更新
    3. 边 (Edge)：节点之间的转移关系
    4. MemorySaver：跨调用持久化对话状态

本图：retrieve → generate（两个节点，一条边）

运行方式：
    python examples/09_langgraph/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_chroma import Chroma  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_huggingface import HuggingFaceEmbeddings  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402
from langgraph.graph import END, START, StateGraph  # noqa: E402

from utils.llm import get_chat_model  # noqa: E402

CHROMA_DIR = Path(__file__).resolve().parent / "chroma"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


# ============ State 定义 ============
class RAGState(TypedDict):
    """工作流的全局状态。

    LangGraph 的状态是一个 TypedDict，每个节点返回"部分字段"的更新。
    """

    question: str           # 用户问题
    documents: list[str]    # 检索到的文档片段
    answer: str             # 最终回答


# ============ 节点定义 ============
def retrieve_node(state: RAGState) -> dict:
    """节点 1：从 Chroma 检索相关文档。"""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="langchain_examples",
    )
    docs = vectorstore.similarity_search(state["question"], k=2)
    return {"documents": [d.page_content for d in docs]}


def generate_node(state: RAGState) -> dict:
    """节点 2：基于检索到的文档生成回答。"""
    llm = get_chat_model()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "请基于背景信息回答问题。如果背景信息不足，请直说不知道。\n\n背景信息：\n{context}",
            ),
            ("human", "{question}"),
        ]
    )
    chain = prompt | llm | StrOutputParser()
    # 用 .get 兜底：避免 LangGraph 1.0 + MemorySaver 在多次 invoke 间的 state 传递偶发问题
    context = "\n\n".join(state.get("documents") or [])
    answer = chain.invoke({"context": context, "question": state["question"]})
    return {"answer": answer}


# ============ 图定义 ============
def build_graph():
    """构造并编译状态图。"""
    workflow = StateGraph(RAGState)

    # 添加节点
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    # 添加边：START → retrieve → generate → END
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    # MemorySaver 让 graph 可以按 thread_id 持久化状态
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app


def main() -> None:
    print("=" * 60)
    print("[LangGraph] retrieve → generate 工作流")
    print("=" * 60)

    app = build_graph()

    questions = [
        "Python 是哪一年发布的？",
        "LangChain 的核心思想是什么？",
    ]

    # thread_id 让多次 invoke 共享同一份状态历史
    config = {"configurable": {"thread_id": "demo-thread-1"}}

    for q in questions:
        print(f"\n问题: {q}")
        result = app.invoke({"question": q}, config=config)
        print(f"回答: {result['answer']}")

    print(f"\n（状态历史保存在 MemorySaver 中，thread_id={config['configurable']['thread_id']}）")
    print("  下次调用用相同 thread_id 即可延续状态。\n")


if __name__ == "__main__":
    main()