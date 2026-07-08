# LangChain 学习合集

一个渐进式的中文 LangChain 学习项目，使用 [MiniMax-M3](https://api.minimaxi.com/v1) 作为模型提供方（OpenAI 兼容协议）。从基础调用一路走到 LangGraph 与流式/异步，每个示例独立可跑。

## 快速开始

### 1. 准备 Python 环境

需要 Python ≥ 3.10。建议使用虚拟环境：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

> ⚠️ **常见坑**：PyCharm 会自动创建并使用项目自己的 `.venv/`。在 PyCharm 的 Terminal 里直接 `pip install` 会装到 `.venv`，没问题；但在系统 cmd / 另一个终端里跑 `pip install` 会装到**全局 Python**，PyCharm 仍然找不到。
>
> 如果你看到 `ModuleNotFoundError: No module named 'dotenv'`，多半就是这个原因。修法：
> ```bash
> # Windows
> .venv\Scripts\python.exe -m pip install -r requirements.txt
> # macOS / Linux
> .venv/bin/python -m pip install -r requirements.txt
> ```

### 2. 安装依赖

**确保在虚拟环境激活状态下**（或在 `.venv` 路径下显式调用 `python -m pip`）：

```bash
pip install -r requirements.txt
```

> ⚠️ 首次安装会比较大（LangChain 生态 + 后续 RAG 示例的 embedding 模型）。

### 3. 配置 MiniMax API Key

```bash
# Windows (PowerShell)
copy .env.example .env
# macOS / Linux
cp .env.example .env
```

编辑刚生成的 `.env`，把三个占位符替换为：

| 变量 | 说明 | 示例 |
|---|---|---|
| `MINIMAX_API_KEY` | 你的 MiniMax API Key（**绝不能提交到 git 或聊天工具**） | `sk-cp-...` |
| `MINIMAX_BASE_URL` | MiniMax 提供的 OpenAI 兼容 endpoint | `https://api.minimaxi.com/v1` |
| `MINIMAX_MODEL` | 要调用的模型名 | `MiniMax-M3` |

### 4. 跑第一个示例

```bash
cd examples/01_hello_llm
python main.py
```

应当看到模型对 "Hello" 的回复。

## 示例列表（按推荐学习顺序）

| # | 目录 | 一句话 |
|---|---|---|
| 00 | [`examples/00_credentials`](examples/00_credentials) | 凭据管理：理解 `.env` 加载原理与安全准则 |
| 01 | [`examples/01_hello_llm`](examples/01_hello_llm) | 第一次对话：基础 `invoke` 与流式输出 |
| 02 | [`examples/02_prompt_template`](examples/02_prompt_template) | Prompt 模板：变量替换、消息角色、Few-shot |
| 03 | [`examples/03_lcel_chain`](examples/03_lcel_chain) | LCEL：用 `|` 拼装 LangChain 推荐的现代链 |
| 04 | [`examples/04_output_parser`](examples/04_output_parser) | 输出解析：JSON 与 Pydantic 结构化输出 |
| 05 | [`examples/05_conversation`](examples/05_conversation) | 多轮对话：手动管理 `HumanMessage`/`AIMessage` 历史 |
| 06 | [`examples/06_rag_basics`](examples/06_rag_basics) | RAG 入门：加载 → 切分 → 检索 → 生成 |
| 07 | [`examples/07_rag_vectorstore`](examples/07_rag_vectorstore) | RAG 进阶：Chroma 持久化向量库 |
| 08 | [`examples/08_agent_tools`](examples/08_agent_tools) | Agent：自定义工具 + ReAct 推理 |
| 09 | [`examples/09_langgraph`](examples/09_langgraph) | LangGraph：状态化工作流 |
| 10 | [`examples/10_streaming_async`](examples/10_streaming_async) | 流式 / 异步 / 回调 |

## 项目结构

```
.
├── README.md                   ← 本文件
├── requirements.txt
├── .env.example                ← 环境变量模板（不含真实 key）
├── .gitignore
│
├── utils/
│   └── llm.py                  ← 统一 ChatModel 工厂（所有示例都从这里 import）
│
└── examples/
    ├── 00_credentials/
    ├── 01_hello_llm/
    ├── ...
    └── 10_streaming_async/
```

## 设计原则

- **统一入口**：`utils/llm.py` 是唯一的模型初始化点。切换模型或修改 endpoint 只需改这一个文件。
- **凭据安全**：所有敏感信息走 `.env`，绝不硬编码、绝不提交。
- **独立可跑**：每个示例目录自带 `main.py`，`python main.py` 即可运行。
- **渐进式编号**：`00_` ~ `10_` 按学习顺序排列，目录列表即学习路径。

## 已知限制

- **API 协议细节**：MiniMax-M3 对 LangChain 0.3 全部特性的支持情况，需要在 `examples/08`（Agent tool calling）和 `examples/10`（流式）首次实跑后确认。验证结果会写回对应示例 README 的"已知限制"小节。
- **Embedding 模型**：默认使用 HuggingFace 本地模型（`examples/06/07` 首次运行会下载），避开对 MiniMax embedding 接口的未知假设。

## 常见问题

**Q: 跑示例时报 `EnvironmentError: 缺少环境变量 ...`？**
A: 检查 `.env` 是否存在于仓库根目录，且 `python-dotenv` 已安装（`pip show python-dotenv`）。

**Q: 想换模型怎么办？**
A: 编辑 `utils/llm.py` 中的 `get_chat_model()`，或者直接改 `.env` 里的 `MINIMAX_MODEL`。

**Q: examples/06/07 跑得很慢？**
A: 首次运行会下载 HuggingFace embedding 模型（约 100MB）。后续会走本地缓存。

## 参考文档

- [LangChain 官方文档（中文）](https://python.langchain.ac.cn/)
- [LangChain OpenAI 集成](https://python.langchain.com/docs/integrations/chat/openai)
- [LCEL 编程指南](https://python.langchain.com/docs/concepts/lcel)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)