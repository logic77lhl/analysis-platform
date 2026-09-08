"""分析平台 —— 唯一入口。

启动：streamlit run app.py
新工具：在 tools/ 下新建目录 + meta.yaml 即自动注册，无需改本文件。
"""
import streamlit as st

from core import registry, store
from core.home import make_home_render
from core.ui import load_css

st.set_page_config(page_title="分析平台", page_icon="📊", layout="wide")
load_css()
store.init()  # 确保数据目录与 SQLite 表存在（幂等）

tools = registry.discover_tools()

# 构建各工具页面（slug 作为 URL 路径）
pages: list = []
page_map: dict = {}
for t in tools:
    page = st.Page(t.render, title=t.title, icon=t.icon, url_path=t.slug)
    pages.append(page)
    page_map[t.slug] = page

# 首页：工具目录卡片，可点击跳转
home_page = st.Page(
    make_home_render(page_map, tools),
    title="首页", icon="🏠", url_path="home", default=True,
)

# 按分组组织侧边栏导航
nav: dict = {"平台": [home_page]}
for t in tools:
    nav.setdefault(t.group, []).append(page_map[t.slug])

st.navigation(nav).run()
