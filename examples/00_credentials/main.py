"""示例 00：凭据管理。

本示例不调用任何 LLM，仅演示：
    1. 仓库根目录的 .env 是否被 python-dotenv 正确加载
    2. 三个必需环境变量的就绪状态
    3. 缺失时给出可操作的错误提示

运行方式（在仓库根目录）：
    python examples/00_credentials/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Windows 默认 stdout 是 GBK，无法输出 ✗ 等符号。
# 强制 UTF-8 让所有终端都能正确显示。
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# 把仓库根目录加入 sys.path，使得 `from utils.xxx import ...` 可用。
# 示例从 examples/00_credentials/ 运行也能正确导入顶层 utils 包。
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.llm import env_summary  # noqa: E402


def main() -> None:
    """打印三个必需环境变量的状态（绝不打印真实 key 明文）。"""
    print("=" * 60)
    print("MiniMax 凭据检查")
    print("=" * 60)

    summary = env_summary()
    all_set = True
    for name, state in summary.items():
        marker = "✓" if "<set" in state else "✗"
        print(f"  {marker}  {name}: {state}")
        if "<missing>" in state:
            all_set = False

    print("-" * 60)
    if all_set:
        print("✓ 所有环境变量已就绪。可以继续运行后续示例。")
        print("  提示：examples/01_hello_llm 是第一个会真正调用模型的示例。")
    else:
        print("✗ 缺少必需的环境变量。请按以下步骤修复：")
        print("    1. 在仓库根目录执行：cp .env.example .env")
        print("    2. 编辑 .env，把占位符替换为真实值")
        print("    3. 重新运行本示例")
        sys.exit(1)


if __name__ == "__main__":
    main()