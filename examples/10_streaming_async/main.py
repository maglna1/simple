"""示例 10：流式 / 异步 / 回调。

三件事放在一起：
    1. 同步流式：llm.stream() —— 逐 chunk 输出
    2. 异步调用：await llm.ainvoke() —— 在异步上下文中调用
    3. 自定义回调：BaseCallbackHandler 子类，统计 token 与首字延迟

运行方式：
    python examples/10_streaming_async/main.py
"""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langchain_core.callbacks import BaseCallbackHandler  # noqa: E402

from utils.llm import get_chat_model  # noqa: E402


# ============ 自定义回调：统计 token + 首字延迟 ============
class MetricsCallback(BaseCallbackHandler):
    """记录每个 LLM 调用的 token 消耗与首字延迟。"""

    def __init__(self) -> None:
        self.start_time: float | None = None
        self.first_chunk_time: float | None = None
        self.input_tokens: int = 0
        self.output_tokens: int = 0

    def on_llm_start(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        self.start_time = time.perf_counter()
        self.first_chunk_time = None

    def on_llm_new_token(self, token: str, **kwargs) -> None:  # type: ignore[no-untyped-def]
        # 第一个 token 到达的时间
        if self.first_chunk_time is None and self.start_time is not None:
            self.first_chunk_time = time.perf_counter()

    def on_llm_end(self, response, **kwargs) -> None:  # type: ignore[no-untyped-def]
        try:
            usage = response.generations[0][0].message.usage_metadata
            if usage:
                self.input_tokens = usage.get("input_tokens", 0)
                self.output_tokens = usage.get("output_tokens", 0)
        except (AttributeError, IndexError):
            pass

    def report(self, label: str) -> None:
        """打印本次调用的统计指标。"""
        if self.start_time is None:
            return
        total = time.perf_counter() - self.start_time
        ttft = (
            (self.first_chunk_time - self.start_time)
            if self.first_chunk_time is not None
            else total
        )
        print(f"\n[指标 - {label}]")
        print(f"  首字延迟 (TTFT): {ttft:.3f}s")
        print(f"  总耗时: {total:.3f}s")
        print(f"  input tokens: {self.input_tokens}")
        print(f"  output tokens: {self.output_tokens}")


# ============ 演示 1：同步流式 ============
def demo_sync_stream() -> None:
    """演示 1：同步 stream() —— 逐 chunk 输出。"""
    print("=" * 60)
    print("[演示 1] 同步流式")
    print("=" * 60)

    metrics = MetricsCallback()
    llm = get_chat_model().with_config({"callbacks": [metrics]})

    print("\n回复（流式）: ", end="", flush=True)
    for chunk in llm.stream("用三句话介绍异步编程的优势。"):
        print(chunk.content, end="", flush=True)
    print()
    metrics.report("同步流式")


# ============ 演示 2：异步调用 ============
async def demo_async() -> None:
    """演示 2：异步 ainvoke() —— 在 async 上下文调用。"""
    print("=" * 60)
    print("[演示 2] 异步 ainvoke")
    print("=" * 60)

    metrics = MetricsCallback()
    llm = get_chat_model().with_config({"callbacks": [metrics]})

    response = await llm.ainvoke("用一句话介绍 asyncio。")
    print(f"\n回复: {response.content}")
    metrics.report("异步 ainvoke")


# ============ 演示 3：异步流式 ============
async def demo_async_stream() -> None:
    """演示 3：异步流式 + 并发调用。"""
    print("=" * 60)
    print("[演示 3] 异步流式 + 并发")
    print("=" * 60)

    llm = get_chat_model()
    questions = [
        "Python 的 GIL 是什么？",
        "为什么需要异步？",
        "协程与线程的区别？",
    ]

    async def stream_one(q: str) -> str:
        """异步流式获取一个回答，拼成完整字符串。"""
        chunks: list[str] = []
        async for chunk in llm.astream(q):
            chunks.append(chunk.content)
        return "".join(chunks)

    # 用 asyncio.gather 并发跑三条流式调用
    t0 = time.perf_counter()
    answers = await asyncio.gather(*(stream_one(q) for q in questions))
    elapsed = time.perf_counter() - t0

    print(f"\n并发 3 个问题的总耗时: {elapsed:.2f}s\n")
    for q, a in zip(questions, answers):
        print(f"Q: {q}")
        print(f"A: {a[:80]}{'...' if len(a) > 80 else ''}\n")


def main() -> None:
    demo_sync_stream()
    asyncio.run(demo_async())
    asyncio.run(demo_async_stream())


if __name__ == "__main__":
    main()