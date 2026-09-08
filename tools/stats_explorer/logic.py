"""数据速览 —— 纯计算逻辑，可脱离 UI 复用（CLI / 批量 / 单元测试）。"""
from __future__ import annotations

import io

import pandas as pd
import plotly.express as px


def _read_file(file: dict) -> pd.DataFrame:
    """file: {"name": str, "bytes": bytes}（由平台从 UploadedFile 转换而来）"""
    name, data = file["name"].lower(), file["bytes"]
    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(data))
    if name.endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(data))
    raise ValueError(f"不支持的文件类型: {file['name']}")


def analyze(params: dict) -> dict:
    file, bins = params["file"], int(params["bins"])
    df = _read_file(file)
    num = df.select_dtypes("number")
    if num.empty:
        raise ValueError("文件中没有数值列，无法统计")

    summary = num.describe().T.reset_index().rename(columns={"index": "列名"})

    col = num.columns[0]
    fig = px.histogram(num, x=col, nbins=bins, title=f"「{col}」分布")

    return {
        "metrics": {"行数": len(df), "总列数": df.shape[1], "数值列": num.shape[1]},
        "summary": summary,
        "fig": fig,
        "csv": ("summary.csv", summary.to_csv(index=False).encode("utf-8-sig")),
    }
