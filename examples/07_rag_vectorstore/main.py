"""示例 07：RAG + Chroma 持久化。

把 examples/06 的内存 FAISS 向量库替换为本地 Chroma：
- 首次运行：建立索引，写入 ./chroma 目录
- 后续运行：直接从 ./chroma 加载，无需重新 embedding

运行方式：
    python examples/07_rag_vectorstore/main.py

清理向量库：删除 ./chroma 目录即可
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_chroma import Chroma  # noqa: E402
from langchain_community.document_loaders import TextLoader  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.runnables import RunnablePassthrough  # noqa: E402
from langchain_huggingface import HuggingFaceEmbeddings  # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: E402

from utils.llm import get_chat_model  # noqa: E402

SAMPLE_DOC = Path(__file__).resolve().parent / "sample.txt"
CHROMA_DIR = Path(__file__).resolve().parent / "chroma"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def format_docs(docs) -> str:  # type: ignore[no-untyped-def]
    return "\n\n".join(doc.page_content for doc in docs)


def build_or_load_vectorstore() -> Chroma:
    """如果 ./chroma 不存在则新建索引；存在则直接加载。"""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    if CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir()):
        print(f"  发现已有 Chroma 索引，从 {CHROMA_DIR.name}/ 直接加载")
        return Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=embeddings,
            collection_name="langchain_examples",
        )

    print(f"  首次运行：构建 Chroma 索引到 {CHROMA_DIR.name}/")
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    loader = TextLoader(str(SAMPLE_DOC), encoding="utf-8")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40)
    splits = text_splitter.split_documents(documents)
    print(f"  文档片段数: {len(splits)}")

    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="langchain_examples",
    )
    return vectorstore


def main() -> None:
    print("=" * 60)
    print("[RAG + Chroma] 持久化向量库")
    print("=" * 60)

    print(f"\n[Step] 准备向量库（embedding: {EMBEDDING_MODEL_NAME}）")
    print("  （首次运行会下载 embedding 模型，约 100MB）")
    vectorstore = build_or_load_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "请基于下面提供的背景信息回答问题。如果背景信息不足，请直说不知道。\n\n"
                "背景信息：\n{context}",
            ),
            ("human", "{question}"),
        ]
    )
    llm = get_chat_model()
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    questions = [
        "Python 由谁创建？",
        "常见的向量库有哪些？",
    ]
    for q in questions:
        print(f"\n问题: {q}")
        answer = rag_chain.invoke(q)
        print(f"回答: {answer}")

    # 展示检索到的具体片段（解释 RAG 内部发生了什么）
    print("\n[附] 检索片段可视化（最后一个问题的 top-3 片段）")
    docs = retriever.invoke(questions[-1])
    for i, d in enumerate(docs, 1):
        preview = d.page_content.replace("\n", " ")[:80]
        print(f"  {i}. {preview}...")

    # 清理
    print("\n（清理）如需重新构建索引，删除 ./chroma 目录后再次运行本脚本。")
    print(f"  索引位置: {CHROMA_DIR}\n")


if __name__ == "__main__":
    try:
        main()
    finally:
        # 如果你不想保留索引，可以把下面这行注释掉
        # shutil.rmtree(CHROMA_DIR, ignore_errors=True)
        pass