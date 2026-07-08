"""统一 ChatModel 工厂。

所有示例都应该从这里导入 ChatModel，而不是自己构造 ChatOpenAI。
这样切换模型、改 base_url、注入 mock 等只需要修改这一个文件。

典型用法：

    from utils.llm import get_chat_model

    llm = get_chat_model()                    # 默认 temperature=0.7
    resp = llm.invoke("你好")
    print(resp.content)

设计要点：
    1. 通过 python-dotenv 加载仓库根目录的 .env 文件。
    2. 启动时校验三个必需的环境变量，缺失时给出可操作的错误。
    3. 用 @lru_cache 缓存实例，按 temperature 维度分别缓存。
    4. 因为 MiniMax 提供 OpenAI 兼容协议，直接复用 langchain_openai.ChatOpenAI。
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载 .env：默认从当前工作目录向上找 .env。如果示例从 examples/NN_xxx/ 目录运行，
# python-dotenv 也会向上搜索到仓库根目录。
load_dotenv()

# 必需的三个环境变量。改动这里请同步更新 .env.example 与顶层 README。
_REQUIRED_ENV = ("MINIMAX_API_KEY", "MINIMAX_BASE_URL", "MINIMAX_MODEL")


def _check_env() -> None:
    """检查必需的环境变量；缺失时抛出带可操作提示的 EnvironmentError。"""
    missing = [name for name in _REQUIRED_ENV if not os.environ.get(name)]
    if missing:
        raise EnvironmentError(
            "缺少必需的环境变量："
            f"{', '.join(missing)}\n"
            "请按以下步骤修复：\n"
            "  1. 复制 .env.example 到 .env（仓库根目录）\n"
            "  2. 编辑 .env，把占位符替换为真实的 MiniMax 凭据\n"
            "  3. 重新运行示例"
        )


@lru_cache(maxsize=8)
def get_chat_model(temperature: float = 0.7) -> ChatOpenAI:
    """获取（或复用缓存中的）ChatOpenAI 实例。

    参数：
        temperature: 采样温度，0 表示更确定性的输出，1 表示更有创造性。

    返回：
        已配置好 model / api_key / base_url 的 ChatOpenAI 实例。

    抛出：
        EnvironmentError: 三个必需的环境变量任意一个缺失。
    """
    _check_env()

    return ChatOpenAI(
        model=os.environ["MINIMAX_MODEL"],
        api_key=os.environ["MINIMAX_API_KEY"],
        base_url=os.environ["MINIMAX_BASE_URL"],
        temperature=temperature,
    )


def get_streaming_chat_model(temperature: float = 0.7) -> ChatOpenAI:
    """返回一个开启了 streaming 的 ChatModel 实例。

    注意：底层调用方需要迭代 `.stream()` 返回的 chunk，而不是直接 `.invoke()`。
    """
    return get_chat_model(temperature=temperature)


def env_summary() -> dict[str, str]:
    """返回当前环境变量配置的安全摘要（key 值只显示长度，不显示明文）。

    用法：用于 examples/00_credentials 中向用户确认配置状态。
    """
    summary: dict[str, str] = {}
    for name in _REQUIRED_ENV:
        value = os.environ.get(name, "")
        if value:
            summary[name] = f"<set, len={len(value)}>"
        else:
            summary[name] = "<missing>"
    return summary