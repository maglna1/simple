# langchain-examples Specification

## Purpose
TBD - created by archiving change add-langchain-examples. Update Purpose after archive.
## Requirements
### Requirement: 统一的 ChatModel 工厂入口

系统 SHALL 提供 `utils/llm.py` 模块，作为所有示例获取 `ChatModel` 的唯一入口。

#### Scenario: 示例从统一入口获取模型
- **WHEN** 任意示例调用 `get_chat_model()`
- **THEN** 返回一个 `ChatOpenAI` 实例，其 `model`、`api_key`、`base_url` 三个字段分别来自 `MINIMAX_MODEL`、`MINIMAX_API_KEY`、`MINIMAX_BASE_URL` 环境变量

#### Scenario: 工厂函数按参数缓存实例
- **WHEN** 同一进程以相同参数两次调用 `get_chat_model(temperature=0.7)`
- **THEN** 第二次调用返回的对象与第一次是同一个实例（命中缓存）

### Requirement: 启动时校验必需环境变量

系统 SHALL 在工厂函数被调用时校验 `MINIMAX_API_KEY`、`MINIMAX_BASE_URL`、`MINIMAX_MODEL` 是否齐全，并在缺失时抛出友好错误。

#### Scenario: 缺失 API Key 时给出可操作错误
- **WHEN** 进程环境未设置 `MINIMAX_API_KEY` 且 `get_chat_model()` 被调用
- **THEN** 抛出 `EnvironmentError`，错误消息明确列出缺失变量名并提示复制 `.env.example` 到 `.env`

### Requirement: 凭据通过 .env 文件管理

系统 SHALL 通过 `python-dotenv` 自动加载仓库根目录的 `.env`，且 SHALL 在仓库中提供 `.env.example` 模板。

#### Scenario: .env 被自动读取
- **WHEN** 示例进程启动且仓库根目录存在 `.env`
- **THEN** `.env` 中的键值对被加载到 `os.environ`

#### Scenario: 提供 .env.example 模板
- **WHEN** 仓库被克隆
- **THEN** 根目录存在 `.env.example`，列出所有必需变量名（值为占位符），但不包含任何真实 key

### Requirement: 真实凭据不得进入版本控制

系统 MUST 将 `.env` 加入 `.gitignore`。

#### Scenario: .env 不出现在 git 状态中
- **WHEN** 在仓库内执行 `git status`
- **THEN** `.env` 不出现在未跟踪文件列表中

### Requirement: 每个示例独立可跑

每个示例 SHALL 仅需 `pip install -r requirements.txt` 与配置 `.env` 后，通过 `python main.py` 即可运行，不需要额外的手工配置。

#### Scenario: hello_llm 示例独立运行
- **WHEN** 用户执行 `cd examples/01_hello_llm && python main.py`
- **THEN** 程序输出 MiniMax-M3 对提示词 "Hello" 的回复内容

### Requirement: 示例内容中文

所有示例源代码的注释与每个示例的 `README.md` SHALL 使用简体中文；标识符与依赖名使用英文。

#### Scenario: 示例 README 是简体中文
- **WHEN** 阅读任一 `examples/NN_xxx/README.md`
- **THEN** 自然语言内容为简体中文

#### Scenario: 代码注释是简体中文
- **WHEN** 阅读任一 `examples/NN_xxx/main.py`
- **THEN** 非字符串字面量的注释使用简体中文

### Requirement: 渐进式编号的目录布局

示例目录 SHALL 使用两位数字前缀 `00_` ~ `10_` 命名，按推荐学习顺序排列。

#### Scenario: 目录按序排列
- **WHEN** 在 `examples/` 下执行 `ls`
- **THEN** 目录顺序依次为 `00_credentials`、`01_hello_llm`、`02_prompt_template`、`03_lcel_chain`、`04_output_parser`、`05_conversation`、`06_rag_basics`、`07_rag_vectorstore`、`08_agent_tools`、`09_langgraph`、`10_streaming_async`

### Requirement: 11 个示例目录全部存在

系统 SHALL 提供恰好 11 个编号示例目录，对应"凭据管理"以及 10 个 LangChain 主题。

#### Scenario: 示例目录完整
- **WHEN** 在 `examples/` 下执行 `ls -d ??_*`
- **THEN** 输出包含全部 11 个目录名（见上一条 Scenario 列表）

### Requirement: 顶层 README 总览

系统 SHALL 在仓库根目录提供 `README.md`，列出所有 11 个示例，每条带一句话说明并链接到对应目录。

#### Scenario: 顶层 README 列出全部示例
- **WHEN** 阅读仓库根目录 `README.md`
- **THEN** 看到 11 个示例的列表，顺序与目录顺序一致

### Requirement: 依赖完整声明

系统 SHALL 在 `requirements.txt` 中声明所有必需的 Python 包。

#### Scenario: 安装依赖后无 ModuleNotFoundError
- **WHEN** 用户在干净虚拟环境中执行 `pip install -r requirements.txt` 成功后，运行任意示例
- **THEN** 示例不抛 `ModuleNotFoundError`

### Requirement: 现有 main.py 不被修改

系统 MUST NOT 修改仓库根目录现有的 `main.py`。

#### Scenario: main.py 内容保持不变
- **WHEN** 在变更前后分别读取 `main.py`
- **THEN** 两次读取得到的字节内容完全一致

### Requirement: utils/llm.py 是唯一的模型初始化点

系统 SHALL 不在任何示例的 `main.py` 中直接调用 `ChatOpenAI(...)` 构造器；所有示例必须通过 `utils/llm.get_chat_model()` 获取模型。

#### Scenario: 示例不直接构造 ChatOpenAI
- **WHEN** 在 `examples/` 下执行 grep，搜索模式 `ChatOpenAI(`
- **THEN** 仅匹配出现在 `utils/llm.py` 内的定义点，示例目录下零匹配

