## Context

仓库当前仅包含 PyCharm 默认生成的 `main.py`，是空白起步状态。

- **目标用户**：开发者本人及其团队，希望渐进式掌握 LangChain。
- **运行环境**：Python ≥ 3.10，本机 Windows（PyCharm 已就绪），无 Docker / CI / 部署诉求。
- **模型提供方**：MiniMax-M3，通过 `https://api.minimaxi.com/v1` 提供 OpenAI 兼容的 Chat Completions 接口。鉴权走标准 `Authorization: Bearer <key>`。
- **依赖管理器**：使用 `requirements.txt`（暂不引入 `poetry` / `uv`，避免新概念叠加学习负担）。
- **Schema**：`spec-driven`，需要同时落 `proposal.md`、`design.md`、`specs/`、`tasks.md` 四个工件。

## Goals / Non-Goals

**Goals:**

- 提供 10 个渐进式中文示例，覆盖 LangChain 主要能力面（基础调用 → LCEL → 输出解析 → 多轮对话 → RAG → 向量库 → Agent → LangGraph → 流式/异步）。
- 通过 `utils/llm.py` 统一模型入口，避免每个示例重复样板代码。
- 凭据管理通过 `.env` + `python-dotenv`，在 `examples/00_credentials/` 中给出标准示范。
- 每个示例独立可跑（`python main.py`），自带中文 README 说明目标与关键概念。
- 顶层 `README.md` 提供总览，让读者按顺序学习。

**Non-Goals:**

- 不构建生产级项目脚手架（无 Dockerfile、无 CI、无日志框架、无错误上报）。
- 不做多模型动态切换（仅 MiniMax-M3，切换模型的扩展点保留为后续）。
- 不引入 LangServe / LangSmith / LangChain Hub。
- 不写单元测试（示例代码以"能跑通"为目标，测试会冲淡学习焦点）。
- 不修改现有 `main.py`（保留 PyCharm 模板，避免 IDE 行为变化）。
- 不写自动补全脚本或依赖锁定脚本（如 `pip freeze` → `requirements.txt` 的反向生成）。

## Decisions

### 1. 使用 `langchain_openai.ChatOpenAI` + 自定义 `base_url`

**选择**：直接使用官方 `langchain-openai` 包，把 `base_url` 指向 MiniMax。

**理由**：

- MiniMax 提供的是 OpenAI 兼容协议，复用官方 SDK 零自定义代码。
- `langchain-openai` 是 LangChain 维护的核心集成，版本升级兼容性较好。
- 协议不兼容时只需修改 `utils/llm.py` 一处，10 个示例无感知。

**备选方案**：

- 自定义 `BaseChatModel` 子类：协议不完全明确前会过度设计，否决。
- 直接 `requests` 调 HTTP：丢掉 LangChain 全部中间件能力（callbacks、流式、批处理），否决。

### 2. 依赖管理使用 `requirements.txt`

**理由**：与现有 PyCharm 项目习惯一致；不引入新概念；后续若需要可平滑迁移到 `uv` / `poetry`。

**锁版本策略**：使用 `>=` 最小版本约束，并固定到 LangChain 0.3 生态；不锁小版本（避免阻塞次要升级）。

### 3. `utils/llm.py` 暴露 `get_chat_model()` 工厂函数

**理由**：

- 工厂函数 + `@lru_cache` 兼顾"易复用"与"按参数缓存"。
- 单一入口 = 单一改造点。
- 在工厂内做环境变量校验，给出友好错误（缺 key 时直接报，胜过示例里神秘 401）。

**备选方案**：

- 全局单例 `LLM`：参数化（temperature、model 切换）不灵活。
- 每个示例独立初始化：违反"统一入口"原则。

### 4. 目录布局：`utils/` + `examples/NN_topic/`

**理由**：

- 编号前缀 `00_` ~ `10_` 自然排序，方便读者按序学习。
- 每个示例独立目录，自带 README，符合"渐进式"目标。
- 顶层 `utils/` 与 LangChain 自身源码风格一致，降低认知切换成本。

**备选方案**：

- 单文件巨型 `main.py`：可读性差，否决。
- 按主题分子包（`chains/`、`rag/`、`agents/`）：跨子包共享 `utils` 反向依赖麻烦，否决。

### 5. RAG 默认使用本地 Chroma + HuggingFace Embeddings

**理由**：

- Chroma 本地嵌入式运行，零外部依赖（除首次下载模型）。
- 避免对 MiniMax embedding 接口做未经验证的假设。
- HuggingFace 本地模型可离线运行，更易复现。

**降级路径**：若 `langchain-huggingface` 在国内下载困难，回退到 `langchain_community.embeddings.HuggingFaceBgeEmbeddings`。

### 6. 中文注释 + 英文标识符

**理由**：与现有 `main.py` 注释风格一致；标识符与 LangChain 官方示例对齐，便于检索官方文档。

## Risks / Trade-offs

- **[MiniMax-M3 API 协议细节未完全验证]** → 在 `examples/01_hello_llm/` 第一次实际跑通作为冒烟；不通过则先回头修正 `utils/llm.py`。
- **[LangChain 0.3 → 1.0 期间 import 路径可能 breaking]** → 在 `requirements.txt` 锁 LangChain 主版本为 `>=0.3,<1.0`；1.0 发布后再单独跟进。
- **[MiniMax 是否原生支持 `tools` 参数未知]** → `examples/08_agent_tools/` 实际跑一次确认；不支持时改为提示词模拟 ReAct（说明限制）。
- **[MiniMax 是否支持流式 `stream=True` 未知]** → `examples/01` 与 `examples/10` 验证；若不支持则在 README 标注"该 provider 当前非流式"。
- **[embedding 模型下载可能慢/被墙]** → 在 `examples/06/07` 的 README 提供 HuggingFace 国内镜像环境变量示例。
- **[统一入口导致示例的"魔法"略多]** → `examples/00_credentials/` 专门讲透 `utils/llm.py` 与 `.env` 的协作，作为后续示例的前置知识。

## Migration Plan

不适用——本变更完全新增，不修改任何已有业务代码。

回滚策略：若中途变更被否决，删除以下目录即可，业务侧零影响：

```
utils/
examples/
requirements.txt
.env.example
.gitignore  （追加的部分可手动去除）
README.md
```

## Open Questions

1. MiniMax-M3 是否原生支持 `tools` / `tool_choice` 参数？（影响 `examples/08`）
2. MiniMax-M3 是否原生支持 `stream=True`？（影响 `examples/01` 流式分支与 `examples/10`）
3. MiniMax 是否提供独立的 embedding 接口？若提供，模型名是？（影响 `examples/06/07` 是否可用其 embedding 替代本地模型）
4. 国内网络下，`huggingface.co` 模型下载是否需要镜像？（影响 `examples/06/07` 的依赖安装说明）

以上四个问题在对应示例首次实跑时验证，验证结果写回对应 README 的"已知限制"小节。