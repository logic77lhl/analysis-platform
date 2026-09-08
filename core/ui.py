"""平台通用 UI 组件库 —— 所有工具复用这里的组件，保证风格统一。"""
from __future__ import annotations

import streamlit as st

CSS = """
<style>
    /* ── 设计系统 tokens ─────────────────────────────── */
    :root {
        --bg: #F5F3F0;
        --surface: #FFFFFF;
        --primary: #7C5CFC;
        --primary-hover: #6A4AE8;
        --primary-light: #F1EEFF;
        --text-primary: #161024;
        --text-secondary: #564E6A;
        --text-muted: #9590A4;
        --border: #E6E3EE;
        --success: #0D9F6E;  --success-bg: #ECFDF5;
        --warning: #D97706;  --warning-bg: #FFFBEB;
        --error: #DC2626;    --error-bg: #FEF2F2;
        --radius-lg: 20px; --radius-md: 14px; --radius-sm: 10px; --radius-xs: 6px;
        --shadow-sm: 0 1px 3px rgba(22,16,36,0.06);
        --shadow-md: 0 4px 12px rgba(22,16,36,0.08);
        --shadow-lg: 0 8px 24px rgba(22,16,36,0.1);
    }

    /* 字体：标题 Sora / 正文 DM Sans */
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,700&display=swap');
    html, body, button, input, select, textarea,
    [data-testid="stMarkdownContainer"], [data-testid="stText"] {
        font-family: 'DM Sans', 'Microsoft YaHei', sans-serif;
        color: var(--text-primary);
    }
    h1, h2, h3, h4, .plat-header h2, .plat-hero h2,
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        font-family: 'Sora', 'Microsoft YaHei', sans-serif;
    }
    h2 { color: var(--text-primary); }
    p, span, li { color: var(--text-secondary); }
    .stApp { background: var(--bg); }

    /* 入场轻淡入（rerun 时重播但时长短，不干扰） */
    @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
    .plat-header, .plat-hero { animation: fadeUp .3s ease both; }
    [data-testid="stMetric"], .tool-card { animation: fadeUp .35s ease both; }

    /* ── 页头横幅（浅色：主色浅底 + 左侧主色条） ────── */
    .plat-header, .plat-hero {
        background: var(--primary-light);
        border-left: 4px solid var(--primary);
        border-radius: var(--radius-lg);
        padding: 20px 26px;
        margin: 4px 0 14px 0;
        box-shadow: var(--shadow-sm);
    }
    .plat-hero { padding: 34px 30px; }
    .plat-header h2, .plat-hero h2 { color: var(--text-primary); margin: 0; font-weight: 700; }
    .plat-header p, .plat-hero p { color: var(--text-secondary); margin: 6px 0 0; font-size: 0.92rem; }

    /* ── 工具卡片 ───────────────────────────────────── */
    .tool-card {
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        padding: 16px;
        height: 100%;
        background: var(--surface);
        box-shadow: var(--shadow-sm);
        transition: all 0.18s ease;
    }
    .tool-card:hover {
        transform: translateY(-2px);
        border-color: var(--primary);
        box-shadow: var(--shadow-md);
    }
    .tool-card h4 { margin: 0 0 6px 0; color: var(--text-primary); }
    .tool-card p { color: var(--text-muted); font-size: 0.85rem; min-height: 2.4em; margin: 0; }

    /* ── 指标卡（中卡片圆角 + 悬停阴影） ─────────────── */
    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        box-shadow: var(--shadow-sm);
        transition: box-shadow 0.18s ease;
    }
    div[data-testid="stMetric"]:hover { box-shadow: var(--shadow-md); }
    [data-testid="stMetricValue"] { color: var(--text-primary); }

    /* ── 表格容器 ───────────────────────────────────── */
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }

    /* ── 按钮 ───────────────────────────────────────── */
    button[kind="primary"] { border-radius: var(--radius-sm); }
    button[kind="primary"]:hover { background: var(--primary-hover) !important; }
    button[kind="secondary"], button[kind="tertiary"] {
        border-radius: var(--radius-sm);
        border: 1px solid var(--border);
    }

    /* ── 侧边栏 ─────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 1.4rem; }
    section[data-testid="stSidebar"] * { color: var(--text-secondary); }
    section[data-testid="stSidebar"] a span { color: var(--text-primary); }

    /* 分隔线弱化 */
    hr { border-color: var(--border); }
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
            st.dataframe(val, width='stretch', hide_index=True)
        elif t == "plotly":
            st.plotly_chart(val, width='stretch', key=f"{key_ns}:out:{key}")
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
