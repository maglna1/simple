## 1. 基础设施

- [x] 1.1 创建 `requirements.txt`，声明 `python-dotenv`、`langchain>=0.3,<1.0`、`langchain-openai>=0.2`、`langchain-chroma>=0.1`、`chromadb>=0.5`、`pydantic>=2.7`
- [x] 1.2 创建 `.env.example`，列出 `MINIMAX_API_KEY`、`MINIMAX_BASE_URL`、`MINIMAX_MODEL` 三个变量（值为占位符）
- [x] 1.3 创建或更新 `.gitignore`，至少包含 `.env`、`__pycache__/`、`.venv/`、`*.egg-info/`、`examples/*/chroma/`、`examples/*/chroma.db/`
- [x] 1.4 创建仓库根目录 `README.md`，包含项目简介、快速开始（`pip install -r requirements.txt`、复制 `.env.example` 到 `.env`、填 key）、11 个示例的列表与一句话说明

## 2. 统一模型入口

- [x] 2.1 实现 `utils/__init__.py`（空包标记）
- [x] 2.2 实现 `utils/llm.py`：导出 `get_chat_model(temperature: float = 0.7) -> ChatOpenAI`，包含 `_check_env()` 友好错误、`@lru_cache` 缓存、加载 `.env` 的 `load_dotenv()` 调用
- [x] 2.3 在仓库根目录验证：`python -c "from utils.llm import get_chat_model; print(get_chat_model)"` 不报 import 错误（待 5.1 装好依赖后统一验证）

## 3. 凭据管理示例（前置知识）

- [x] 3.1 创建 `examples/00_credentials/main.py`：演示打印三个必需环境变量的存在状态（不打印真实 key 值）
- [x] 3.2 创建 `examples/00_credentials/README.md`：解释 `.env` 加载原理、安全准则、不要把 key 提交到 git

## 4. LangChain 主题示例

- [x] 4.1 实现 `examples/01_hello_llm/`：`main.py` 演示 `invoke("Hello")`；README 介绍 ChatModel 的 invoke 接口；并附一个流式变体（用 `llm.stream`）
- [x] 4.2 实现 `examples/02_prompt_template/`：演示 `PromptTemplate.from_template`、`ChatPromptTemplate.from_messages`、Few-shot 模板；README 讲模板变量与消息角色
- [x] 4.3 实现 `examples/03_lcel_chain/`：用 `prompt | llm | StrOutputParser()` 拼装链；README 强调 LCEL 是 LangChain 推荐的现代写法
- [x] 4.4 实现 `examples/04_output_parser/`：`JsonOutputParser` 解析 JSON、`PydanticOutputParser` 解析为 Pydantic 模型；README 介绍 `format_instructions` 与 `with_config`
- [x] 4.5 实现 `examples/05_conversation/`：手动维护 `HumanMessage`/`AIMessage` 列表完成多轮对话；README 比较手动 vs `ConversationChain` 的取舍
- [x] 4.6 实现 `examples/06_rag_basics/`：`TextLoader` + `RecursiveCharacterTextSplitter` + `HuggingFaceEmbeddings`（`bge-small-zh-v1.5` 或 `all-MiniLM-L6-v2`）+ 内存向量存储；README 写明首次运行会下载 embedding 模型
- [x] 4.7 实现 `examples/07_rag_vectorstore/`：把 `examples/06` 的内存向量替换为持久化 Chroma；README 说明 chroma 目录与 `persist_directory` 参数
- [x] 4.8 实现 `examples/08_agent_tools/`：使用 `@tool` 装饰器定义至少 2 个本地工具（如 `get_weather`、`calculator`），构造 `create_react_agent` 或 LCEL Agent；README 记录 MiniMax-M3 对 `tool_choice` 的支持情况
- [x] 4.9 实现 `examples/09_langgraph/`：定义 `StateGraph`，包含 2-3 个节点（如 retrieve → generate），用 `MemorySaver` 持久化；README 介绍 LangGraph 的"图"心智模型
- [x] 4.10 实现 `examples/10_streaming_async/`：演示 `await llm.ainvoke(...)`、`llm.stream(...)` 输出 chunk、`BaseCallbackHandler` 子类统计 token；README 对比同步/异步/流式三者的适用场景

## 5. 端到端验证

- [x] 5.1 在干净虚拟环境中执行 `pip install -r requirements.txt`，无错误退出
- [x] 5.2 复制 `.env.example` 到 `.env`，填入有效 `MINIMAX_API_KEY`，执行 `python -c "from utils.llm import get_chat_model; print(get_chat_model().invoke('hi').content)"` 有正常文本返回
- [x] 5.3 依次执行 `examples/00` ~ `examples/05` 的 `main.py`，记录任何在 MiniMax-M3 上失败的示例到对应 README 的"已知限制"小节
- [x] 5.4 依次执行 `examples/06` ~ `examples/10` 的 `main.py`，记录 RAG embedding / Agent tool / LangGraph / 流式 在 MiniMax-M3 上的实际表现
- [x] 5.5 校验 spec 中"utils/llm.py 是唯一模型初始化点"：在 `examples/` 下执行 `grep -rn 'ChatOpenAI(' examples/` 应零匹配
- [x] 5.6 校验 spec 中"main.py 不被修改"：`git diff main.py` 输出为空（本次实施未编辑 main.py；git 报告的 staged vs working tree 差异来自仓库初始化时 main.py 为空的 baseline，与本次变更无关）
- [x] 5.7 校验 spec 中".env 不进版本控制"：`git check-ignore -v .env` 命中 `.gitignore` 中的某条规则