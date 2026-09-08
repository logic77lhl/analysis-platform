"""工具注册与动态发现：扫描 tools/ 目录，按 meta.yaml 声明加载。

三种工具模式：
1. schema 驱动：meta.yaml 里声明 schema: form.yaml，平台自动生成 UI（简单工具）
2. 自由渲染：  工具包里实现 render()，meta.yaml 用 entry 指定（复杂工具）
3. 外链：      meta.yaml 里声明 url，工具跑在独立资源上，平台只放入口
"""
from __future__ import annotations

import importlib
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "tools"

# 加载失败的工具记录于此，首页统一展示，不拖垮整个平台
LOAD_ERRORS: list[tuple[str, str]] = []


@dataclass
class Tool:
    slug: str                                    # URL 标识，须唯一
    title: str
    icon: str
    group: str
    description: str = ""
    url: str | None = None                       # 外链模式
    schema: str | None = None                    # schema 模式的 form 文件名
    dir: Path | None = None
    render: Callable[[], None] | None = None


def _schema_render(tool: Tool) -> Callable[[], None]:
    from core import schema_runner

    def render() -> None:
        schema_runner.run(tool)

    return render


def _link_render(tool: Tool) -> Callable[[], None]:
    import streamlit as st

    def render() -> None:
        st.info(f"该工具部署在独立资源：{tool.url}")
        st.markdown(f"👉 [打开 {tool.title}]({tool.url})")

    return render


def load_tool(tool_dir: Path) -> Tool | None:
    meta_file = tool_dir / "meta.yaml"
    if not meta_file.is_file():
        return None
    meta = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
    tool = Tool(
        slug=meta["slug"],
        title=meta["name"],
        icon=meta.get("icon", "🔧"),
        group=meta.get("group", "其他"),
        description=meta.get("description", ""),
        url=meta.get("url"),
        schema=meta.get("schema"),
        dir=tool_dir,
    )
    if tool.url:
        tool.render = _link_render(tool)
    elif tool.schema:
        tool.render = _schema_render(tool)
    else:
        mod = importlib.import_module(f"tools.{tool_dir.name}.tool")
        tool.render = getattr(mod, meta.get("entry", "render"))
    return tool


def discover_tools(root: Path | None = None) -> list[Tool]:
    """扫描目录加载全部工具；单个工具加载失败只记录，不中断平台启动。"""
    LOAD_ERRORS.clear()
    root = root or TOOLS_DIR
    tools: list[Tool] = []
    if not root.is_dir():
        return tools
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        try:
            tool = load_tool(d)
            if tool:
                tools.append(tool)
        except Exception:
            LOAD_ERRORS.append((d.name, traceback.format_exc(limit=3)))
    slugs = [t.slug for t in tools]
    if len(slugs) != len(set(slugs)):
        raise ValueError(f"meta.yaml slug 重复: {slugs}")
    return tools
