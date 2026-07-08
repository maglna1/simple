# 示例 06：RAG 入门

RAG（Retrieval-Augmented Generation）= 用检索增强生成。核心思路：让 LLM 在回答前先去文档库检索相关片段，把片段连同问题一起喂给模型，从而基于**特定领域知识**回答。

## 运行

```bash
python examples/06_rag_basics/main.py
```

## RAG 四步流程

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 1.加载   │ ─▶ │ 2.切分   │ ─▶ │ 3.向量化 │ ─▶ │ 4.检索+  │
│ TextLoader│   │ Splitter │    │ Embed+Vec│    │  生成    │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Step 1：加载文档

```python
loader = TextLoader("sample.txt", encoding="utf-8")
documents = loader.load()
```

`langchain_community.document_loaders` 还提供 `PyPDFLoader`、`WebBaseLoader`、`NotionDBLoader` 等几十种 loader。

### Step 2：切分文档

```python
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=40)
splits = text_splitter.split_documents(documents)
```

`chunk_size` 控制每段最大字符数，`chunk_overlap` 让相邻片段有少量重叠（避免切断语义）。

### Step 3：向量化 + 向量库

```python
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = FAISS.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
```

- **Embedding 模型**把文本转成高维向量。本示例用 `bge-small-zh-v1.5`（智源开源，中文友好，约 100MB）。
- **向量库**负责相似度检索。本示例用 FAISS（Meta 开源，内存模式，不持久化）。
- `k=3` 表示每次检索返回最相关的 3 个片段。

### Step 4：检索 + 生成（LCEL）

```python
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
```

巧妙之处：

- `{"context": retriever | format_docs, "question": RunnablePassthrough()}` 把字典构造转成一个 Runnable：左边是检索 + 格式化，右边是透传原始问题。
- 这个字典会作为 `prompt` 的输入变量，`context` 来自检索，`question` 来自用户输入。

## 已知限制 / 注意事项

- **首次运行慢**：`bge-small-zh-v1.5` 模型约 100MB，会从 HuggingFace 下载。国内网络可能慢或被墙，可设置 `HF_ENDPOINT=https://hf-mirror.com` 环境变量走镜像。
- **内存向量库**：本示例用 FAISS 内存模式，重启后向量库丢失。`examples/07` 会改用 Chroma 持久化。
- **Embedding 模型选型**：本合集默认使用本地 HuggingFace 模型，避开对 MiniMax embedding 接口的未知假设。

## 下一步

继续学习 [`examples/07_rag_vectorstore`](../07_rag_vectorstore/README.md)：把内存向量库换成持久化 Chroma。