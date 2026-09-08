"""平台通用 UI 组件库 —— 所有工具复用这里的组件，保证风格统一。"""
from __future__ import annotations

import streamlit as st

CSS = """
<style>
    /* 页头横幅 */
    .plat-header, .plat-hero {
        background: linear-gradient(120deg, #1a1a2e 0%, #16213e 55%, #0f3460 100%);
        border-radius: 14px;
        padding: 20px 26px;
        margin: 4px 0 14px 0;
    }
    .plat-hero { padding: 34px 30px; }
    .plat-header h2, .plat-hero h2 { color: #fff; margin: 0; font-weight: 700; }
    .plat-header p, .plat-hero p { color: #c9d1e4; margin: 6px 0 0; font-size: 0.92rem; }

    /* 工具卡片 */
    .tool-card {
        border: 1px solid rgba(120, 120, 128, 0.25);
        border-radius: 12px;
        padding: 16px;
        height: 100%;
        background: rgba(120, 120, 128, 0.05);
        transition: all 0.18s ease;
    }
    .tool-card:hover {
        transform: translateY(-2px);
        border-color: #e94560;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
    }
    .tool-card h4 { margin: 0 0 6px 0; }
    .tool-card p { color: rgba(150, 150, 150, 1); font-size: 0.85rem; min-height: 2.4em; margin: 0; }

    /* 指标卡 */
    div[data-testid="stMetric"] {
        background: rgba(120, 120, 128, 0.08);
        border-radius: 10px;
        padding: 14px 16px;
    }

    /* 侧边栏呼吸感 */
    section[data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
</style>
"""


def load_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title: str, desc: str = "") -> None:
    """统一页头（渐变横幅）。"""
    desc_html = f"<p>{desc}</p>" if desc else ""
    st.markdown(f'<div class="plat-header"><h2>{title}</h2>{desc_html}</div>',
                unsafe_allow_html=True)


def param_form(inputs: list[dict], key_ns: str) -> dict:
    """按 schema 渲染参数表单，返回 {key: value}。须在 st.form 内调用。

    控件 key 统一加工具命名空间前缀，避免跨工具的 session_state 冲突。
    """
    params: dict = {}
    for spec in inputs:
        t = spec["type"]
        key = f"{key_ns}:{spec['key']}"
        label = spec.get("label", spec["key"])
        help_ = spec.get("help")
        if t == "file":
            params[spec["key"]] = st.file_uploader(
                label, type=spec.get("accept"), key=key, help=help_)
        elif t == "text":
            params[spec["key"]] = st.text_input(
                label, value=spec.get("default", ""), key=key, help=help_)
        elif t == "textarea":
            params[spec["key"]] = st.text_area(
                label, value=spec.get("default", ""), key=key, help=help_)
        elif t == "number":
            params[spec["key"]] = st.number_input(
                label,
                value=spec.get("default", 0),
                min_value=spec.get("min"),
                max_value=spec.get("max"),
                step=spec.get("step"),
                key=key, help=help_)
        elif t == "select":
            options = spec.get("options", [])
            default = spec.get("default")
            params[spec["key"]] = st.selectbox(
                label, options,
                index=options.index(default) if default in options else 0,
                key=key, help=help_)
        elif t == "multiselect":
            params[spec["key"]] = st.multiselect(
                label, spec.get("options", []),
                default=spec.get("default"), key=key, help=help_)
        elif t == "checkbox":
            params[spec["key"]] = st.checkbox(
                label, value=spec.get("default", False), key=key, help=help_)
        elif t == "date":
            params[spec["key"]] = st.date_input(label, key=key, help=help_)
        else:
            st.error(f"未知控件类型: {t}")
    return params


def result_card(outputs: list[dict], results: dict, key_ns: str) -> None:
    """按 schema 渲染结果区。

    outputs 元素示例：
      {type: dataframe, key: df, label: 结果表}
      {type: plotly,    key: fig}
      {type: metrics,   key: metrics}          # value 为 dict[str, 数字]
      {type: download,  key: csv}              # value 为 (文件名, bytes)
      {type: text|markdown|json, key: ...}
    """
    for spec in outputs:
        t, key = spec["type"], spec["key"]
        val = results.get(key)
        if val is None:
            continue
        if spec.get("label"):
            st.subheader(spec["label"])
        if t == "dataframe":
            st.dataframe(val, use_container_width=True, hide_index=True)
        elif t == "plotly":
            st.plotly_chart(val, use_container_width=True, key=f"{key_ns}:out:{key}")
        elif t == "text":
            st.write(val)
        elif t == "markdown":
            st.markdown(val)
        elif t == "json":
            st.json(val)
        elif t == "metrics":
            cols = st.columns(max(len(val), 1))
            for col, (name, v) in zip(cols, val.items()):
                col.metric(name, v)
        elif t == "download":
            fname, data = val
            st.download_button("下载结果", data, file_name=fname,
                               key=f"{key_ns}:dl:{key}")
        else:
            st.error(f"未知输出类型: {t}")
