"""示例 06：RAG 入门。

四步完成一次 RAG：
    1. 加载文档（TextLoader）
    2. 切分文档（RecursiveCharacterTextSplitter）
    3. Embedding + 内存向量存储
    4. 检索 + 生成

运行方式：
    python examples/06_rag_basics/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_community.document_loaders import TextLoader  # noqa: E402
from langchain_community.vectorstores import FAISS  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from langchain_core.prompts import ChatPromptTemplate  # noqa: E402
from langchain_core.runnables import RunnablePassthrough  # noqa: E402
from langchain_huggingface import HuggingFaceEmbeddings  # noqa: E402
from langchain_text_splitters import RecursiveCharacterTextSplitter  # noqa: E402

from utils.llm import get_chat_model  # noqa: E402

# 本示例用到的示例文档
SAMPLE_DOC = Path(__file__).resolve().parent / "sample.txt"

# 中文友好的小型 embedding 模型（约 100MB，首次运行会下载）
EMBEDDING_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def format_docs(docs) -> str:  # type: ignore[no-untyped-def]
    """把一组 Document 拼成一段上下文文本。"""
    return "\n\n".join(doc.page_content for doc in docs)


def main() -> None:
    print("=" * 60)
    print("[RAG 入门] 加载 → 切分 → 检索 → 生成")
    print("=" * 60)

    # ============ Step 1: 加载文档 ============
    print(f"\n[Step 1] 加载文档: {SAMPLE_DOC.name}")
    loader = TextLoader(str(SAMPLE_DOC), encoding="utf-8")
    documents = loader.load()
    print(f"  文档数: {len(documents)}, 总字符数: {sum(len(d.page_content) for d in documents)}")

    # ============ Step 2: 切分文档 ============
    print("[Step 2] 切分文档")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40)
    splits = text_splitter.split_documents(documents)
    print(f"  切分后片段数: {len(splits)}")
    for i, s in enumerate(splits[:3], 1):
        preview = s.page_content.replace("\n", " ")[:60]
        print(f"    {i}. {preview}...")

    # ============ Step 3: Embedding + 内存向量库 ============
    print(f"[Step 3] Embedding: {EMBEDDING_MODEL_NAME}")
    print("  （首次运行会下载模型，约 100MB，需要 1-3 分钟）")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_documents(splits, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    print("  向量库已建立")

    # ============ Step 4: RAG 链 ============
    print("[Step 4] 构造 RAG 链")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "请基于下面提供的背景信息回答问题。如果背景信息不足，请直说不知道，不要编造。\n\n"
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

    # ============ 问答 ============
    questions = [
        "LangChain 是什么？",
        "Python 是哪一年发布的？",
        "RAG 解决了什么问题？",
    ]
    for q in questions:
        print(f"\n问题: {q}")
        answer = rag_chain.invoke(q)
        print(f"回答: {answer}\n")


if __name__ == "__main__":
    main()