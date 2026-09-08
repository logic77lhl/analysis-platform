"""文本分析 —— 自由渲染模式：复杂交互自己写 render()。

约定：session_state 的 key 一律加 NS 命名空间前缀，避免与其他工具冲突。
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import store
from core.ui import page_header
from tools.text_stats.logic import count_text

NS = "text-stats"


def render() -> None:
    page_header("文本分析", "粘贴文本，统计字数与词频；可保存结果到历史记录")

    text = st.text_area("文本内容", height=220, key=f"{NS}:text")
    top_n = st.slider("词频 Top-N", 5, 30, 10, key=f"{NS}:top_n")

    c1, c2, _ = st.columns([1, 1, 2])
    run_clicked = c1.button("▶ 分析", type="primary", key=f"{NS}:run")
    save_clicked = c2.button("💾 保存到历史", key=f"{NS}:save",
                             disabled=f"{NS}:result" not in st.session_state)

    if run_clicked:
        if not text.strip():
            st.warning("请先输入文本")
        else:
            st.session_state[f"{NS}:result"] = count_text(text, top_n)

    result = st.session_state.get(f"{NS}:result")
    if result:
        if save_clicked:
            store.record_run(NS, {"chars": result["chars"],
                                  "words": result["words"],
                                  "top_n": top_n})
            st.toast("已保存到历史记录，可在首页查看", icon="💾")

        c1, c2, _ = st.columns(3)
        c1.metric("总字符（去空白）", result["chars"])
        c2.metric("词元数（中文字/英文词）", result["words"])
        st.subheader("词频 Top")
        st.dataframe(pd.DataFrame(result["top"], columns=["词元", "次数"]),
                     use_container_width=True, hide_index=True)
