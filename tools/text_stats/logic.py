"""文本分析 —— 纯计算逻辑。"""
from __future__ import annotations

import re
from collections import Counter


def count_text(text: str, top_n: int = 10) -> dict:
    tokens = re.findall(r"[A-Za-z]+|[\u4e00-\u9fff]", text)
    return {
        "chars": len(re.sub(r"\s", "", text)),
        "words": len(tokens),
        "top": Counter(t.lower() for t in tokens).most_common(top_n),
    }
