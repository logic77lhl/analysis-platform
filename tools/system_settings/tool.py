"""系统设置 —— 用户配置的读写演示。

配置存 DATA_DIR/settings.json；敏感信息（密码/密钥）不要放这里，
走环境变量或 CI/CD secrets 注入。
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import store
from core.ui import page_header

NS = "system-settings"


def render() -> None:
    page_header("系统设置",
                "配置持久化在数据目录，重新部署/重启均不丢失；其他工具通过 store.load_settings() 读取")

    settings = store.load_settings()

    with st.form(f"{NS}:form", border=False):
        org_name = st.text_input("组织名称（显示在首页顶部）",
                                 value=settings.get("org_name", ""),
                                 key=f"{NS}:org")
        keep_history = st.checkbox("记录工具运行历史（首页展示最近记录）",
                                   value=settings.get("keep_history", True),
                                   key=f"{NS}:history")
        if st.form_submit_button("💾 保存设置", type="primary"):
            store.save_settings({"org_name": org_name, "keep_history": keep_history})
            st.success(f"已保存到 {store.SETTINGS_FILE}")
            st.rerun()

    st.divider()
    st.subheader("存储状态")
    c1, c2, c3 = st.columns(3)
    c1.metric("数据目录", str(store.DATA_DIR))
    n_uploads = len(list(store.UPLOADS.glob("*"))) if store.UPLOADS.is_dir() else 0
    c2.metric("已保存上传文件", n_uploads)
    n_runs = len(store.list_runs(limit=10_000))
    c3.metric("历史运行记录", n_runs)

    runs = store.list_runs(limit=10)
    if runs:
        st.subheader("最近运行（存于 SQLite）")
        st.dataframe(
            pd.DataFrame([{"工具": r["tool"],
                           "参数": r["payload"],
                           "时间": r["created_at"]} for r in runs]),
            use_container_width=True, hide_index=True,
        )
