"""平台首页：hero 横幅 + 工具目录卡片 + 最近运行历史。"""
import pandas as pd
import streamlit as st

from core import registry, store


def make_home_render(page_map: dict, tools: list):
    """接收 slug → st.Page 映射，使首页卡片可点击进入对应工具。"""

    def render() -> None:
        org = store.load_settings().get("org_name") or "分析平台"
        st.markdown(
            f'<div class="plat-hero"><h2>📊 {org}</h2>'
            f'<p>所有分析小工具的统一入口 —— 新工具放入 tools/ 目录即自动注册，'
            f'数据持久化在独立目录，重新部署不丢失</p></div>',
            unsafe_allow_html=True)

        for name, err in registry.LOAD_ERRORS:
            with st.expander(f"⚠️ 工具加载失败：{name}"):
                st.code(err)

        by_group: dict[str, list] = {}
        for t in tools:
            by_group.setdefault(t.group, []).append(t)

        for group, group_tools in by_group.items():
            st.subheader(group)
            for i in range(0, len(group_tools), 3):
                cols = st.columns(3)
                for col, t in zip(cols, group_tools[i:i + 3]):
                    with col:
                        st.markdown(
                            f'<div class="tool-card"><h4>{t.icon} {t.title}</h4>'
                            f'<p>{t.description or "（无描述）"}</p></div>',
                            unsafe_allow_html=True)
                        if t.url:
                            st.link_button("打开外部工具", t.url,
                                           width='stretch')
                        elif st.button("进入", key=f"home:go:{t.slug}",
                                       width='stretch'):
                            st.switch_page(page_map[t.slug])

        # ── 最近运行历史（SQLite 持久化） ──
        if store.load_settings().get("keep_history", True):
            runs = store.list_runs(limit=8)
            if runs:
                st.subheader("🕘 最近运行")
                title_map = {t.slug: f"{t.icon} {t.title}" for t in tools}
                st.dataframe(
                    pd.DataFrame([{
                        "工具": title_map.get(r["tool"], r["tool"]),
                        "参数": "，".join(f"{k}={v}" for k, v in r["payload"].items()) or "-",
                        "时间": r["created_at"],
                    } for r in runs]),
                    width='stretch', hide_index=True,
                )

    return render
