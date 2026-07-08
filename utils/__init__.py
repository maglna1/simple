"""工具包：包含所有示例共享的辅助代码。

当前导出：
    - llm.get_chat_model: 统一的 ChatModel 工厂
"""
from __future__ import annotations

import sys

# Windows 默认 stdout 是 GBK，无法输出中文。
# 这里强制 reconfigure，让所有示例的中文 print 正常显示。
# 在 macOS / Linux 上是 no-op，不影响行为。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")