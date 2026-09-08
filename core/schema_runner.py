"""schema 驱动的通用运行器。

流程：读工具的 form.yaml → 自动生成参数表单 → 调用 logic 模块的函数 → 自动渲染结果。
简单工具只需提供 meta.yaml + form.yaml + logic.py，一行 UI 代码都不用写。

内置平台能力：
  - 上传文件自动落盘到 DATA_DIR/uploads（经 store.save_upload）
  - 运行成功自动记录历史到 SQLite（可在系统设置里关闭）
"""
from __future__ import annotations

import importlib

import streamlit as st
import yaml

from core import store, ui


def run(tool) -> None:
    spec = yaml.safe_load((tool.dir / tool.schema).read_text(encoding="utf-8"))

    ui.page_header(tool.title, spec.get("description", tool.description))

    with st.form(f"{tool.slug}:form", border=False):
        params = ui.param_form(spec.get("inputs", []), key_ns=tool.slug)
        submitted = st.form_submit_button("▶ 运行", type="primary",
                                          width='stretch')

    if submitted:
        # UploadedFile → 普通 dict，logic 层不接触 streamlit 对象；
        # 同时落盘到数据目录，重新部署不丢
        for p in spec.get("inputs", []):
            if p["type"] == "file" and params.get(p["key"]) is not None:
                f = params[p["key"]]
                path = store.save_upload(f.name, f.getvalue())
                params[p["key"]] = {"name": f.name, "bytes": f.getvalue(),
                                    "path": str(path)}

        mod_name, _, fn_name = spec["run"].partition(":")
        fn = getattr(importlib.import_module(f"tools.{tool.dir.name}.{mod_name}"),
                     fn_name)
        try:
            with st.spinner("计算中..."):
                results = fn(params) or {}
            st.session_state[f"{tool.slug}:results"] = results

            # 运行历史（可在系统设置中关闭）
            if store.load_settings().get("keep_history", True):
                brief = {k: (v.get("name") if isinstance(v, dict) else v)
                         for k, v in params.items()
                         if isinstance(v, (str, int, float, bool, dict))}
                store.record_run(tool.slug, brief)
        except Exception as e:
            st.error(f"运行失败：{e}")
            st.exception(e)

    # 结果存入 session_state，切换页面后回来不丢失
    if f"{tool.slug}:results" in st.session_state:
        ui.result_card(spec.get("outputs", []),
                       st.session_state[f"{tool.slug}:results"],
                       key_ns=tool.slug)
