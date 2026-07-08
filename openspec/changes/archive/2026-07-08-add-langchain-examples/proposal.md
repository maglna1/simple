## Why

仓库当前仅包含 PyCharm 默认生成的 `main.py`，没有任何可学习的示例代码。为了帮助团队成员渐进式掌握 LangChain 的核心用法（LCEL 链式调用、Prompt 模板、输出解析、记忆、RAG、Agent、LangGraph、流式与异步），需要构建一个**渐进式的中文学习合集**。所有示例通过统一的 `utils/llm.py` 调用 MiniMax-M3（OpenAI 兼容协议，base_url=`https://api.minimaxi.com/v1`），便于随时切换模型或扩展新示例。

## What Changes

- 新增 `utils/llm.py`：统一的 ChatModel 工厂，封装环境变量校验与客户端缓存。
- 新增 `examples/00_credentials/`：演示如何通过 `.env` 管理 MiniMax API Key。
- 新增 `examples/01_hello_llm/`：基础 `invoke` 调用与流式输出。
- 新增 `examples/02_prompt_template/`：`PromptTemplate`、`ChatPromptTemplate`、Few-shot。
- 新增 `examples/03_lcel_chain/`：使用 `|` 操作符组装链。
- 新增 `examples/04_output_parser/`：`JsonOutputParser`、Pydantic 结构化输出。
- 新增 `examples/05_conversation/`：多轮对话与 `HumanMessage`/`AIMessage` 历史管理。
- 新增 `examples/06_rag_basics/`：文档加载、切分、检索、生成。
- 新增 `examples/07_rag_vectorstore/`：Chroma 本地向量库接入。
- 新增 `examples/08_agent_tools/`：ReAct Agent + 自定义 Tool。
- 新增 `examples/09_langgraph/`：状态化工作流。
- 新增 `examples/10_streaming_async/`：流式响应 + 异步 + 回调。
- 新增 `requirements.txt`、`README.md`、`.env.example`、`.gitignore`。
- **保留** 现有 `main.py`（PyCharm 模板不影响新增内容）。

## Capabilities

### New Capabilities

- `langchain-examples`：覆盖 10 个渐进式示例与 `utils/llm.py` 统一入口的端到端学习合集。

### Modified Capabilities

无（仓库当前不存在任何 spec）。

## Impact

- 新增约 30+ 个新文件（10 个示例各 2 个左右 + utils + 配置）。
- 新增 Python 依赖：`python-dotenv`、`langchain`、`langchain-openai`、`langchain-chroma`、`chromadb`、`pydantic`。
- 新增对 MiniMax-M3 API（`https://api.minimaxi.com/v1`）的运行时依赖；首次运行 `examples/06/07/08/09/10` 可能下载 embedding 模型。
- 不修改任何现有业务代码；`main.py` 保持原样。
- 中文文档与中文注释；标识符、依赖名仍使用英文。
- 需要在 `.env` 中配置 `MINIMAX_API_KEY`，并将 `.env` 加入 `.gitignore`。