# 示例 07：RAG + Chroma 持久化

把 `examples/06` 的内存 FAISS 向量库换成 Chroma，向量库会持久化到本地磁盘。

## 运行

```bash
python examples/07_rag_vectorstore/main.py
```

## 与示例 06 的差异

| 维度 | 示例 06（FAISS） | 示例 07（Chroma） |
|---|---|---|
| 持久化 | 内存，重启丢失 | 写到 `./chroma/` 目录 |
| 首次运行 | 构建 + 查询 | 构建 + 查询 |
| 后续运行 | 重新构建 | 直接加载 |
| 元数据过滤 | 不支持 | 支持 |
| 适用规模 | 小（< 10w 片段） | 中等（10w ~ 百万级） |

## 关键代码

### 首次构建

```python
Chroma.from_documents(
    documents=splits,
    embedding=embeddings,
    persist_directory="./chroma",
    collection_name="langchain_examples",
)
```

### 后续加载

```python
Chroma(
    persist_directory="./chroma",
    embedding_function=embeddings,
    collection_name="langchain_examples",
)
```

`collection_name` 是 Chroma 中的"集合"概念，类似数据库里的表名。多个 collection 可以共存于同一个 `persist_directory`。

## 重新构建索引

要刷新数据时：

```bash
rm -rf examples/07_rag_vectorstore/chroma
python examples/07_rag_vectorstore/main.py
```

（Windows PowerShell：`Remove-Item -Recurse -Force examples/07_rag_vectorstore/chroma`）

或者直接编辑 `main.py` 把 `finally` 块里的 `shutil.rmtree(...)` 启用。

## 已知限制

- `chroma/` 目录已经在 `.gitignore` 里忽略，不会被提交。
- 大规模场景应使用 Chroma 的服务端模式（`chromadb.HttpClient`）或换用专用向量库（Pinecone、Milvus、Qdrant）。
- `bge-small-zh-v1.5` embedding 模型仍然在每次启动时由 `HuggingFaceBgeEmbeddings` 加载（约 100MB 内存）。生产环境应单独部署 embedding 服务。

## 下一步

继续学习 [`examples/08_agent_tools`](../08_agent_tools/README.md)：Agent 与自定义工具。