# 分析平台

一个用来装分析工具的 Streamlit 容器：在 `tools/` 下新建一个目录、写一份 `meta.yaml`，它就自动出现在侧边栏和首页。入口文件 `app.py` 不需要动。

它本身不做分析。它解决的是「分析脚本写多了以后长成什么样」——一堆散落的 notebook、参数写死在代码里、换一份数据就要改一遍。

## 它是什么

平台只提供四件事，其余都交给工具自己：

- **注册**：扫 `tools/`，读 `meta.yaml`，自动生成导航和首页卡片
- **参数界面**：`form.yaml` 声明输入，表单自动渲染
- **持久化**：上传文件、运行历史、用户设置统一走 `core/store.py`
- **结果展示**：指标卡、表格、Plotly 图、下载，按 `outputs` 声明渲染

## 三种接入方式

| 模式 | 需要写什么 | 适合 |
|---|---|---|
| **schema 驱动** | `meta.yaml` + `form.yaml` + `logic.py` | 输入简单、输出固定的工具，一行 UI 代码都不用写 |
| **自由渲染** | `meta.yaml`（`entry: render`）+ 自己的 `render()` | 交互复杂、需要多步骤的工具 |
| **外链** | `meta.yaml` 里填 `url` | 跑在独立资源上的服务，平台只放入口 |

## 怎么用

```bash
pip install -r requirements.txt
streamlit run app.py
```

数据默认落在项目下的 `./data`。部署时用 `DATA_DIR` 指向挂载卷，重新发版数据不会丢：

```bash
DATA_DIR=/data streamlit run app.py
```

自带三个工具：**数据速览**（上传 CSV/Excel → 统计摘要、指标卡、首个数值列的分布图）、**文本分析**（中英文字数统计 + 词频 Top-N）、**系统设置**（改配置，写进 `DATA_DIR/settings.json`）。

## 加一个工具

最小形态（schema 驱动）：

```
tools/my_tool/
├── meta.yaml
├── form.yaml
└── logic.py
```

`meta.yaml`：

```yaml
name: 我的工具
slug: my-tool          # URL 标识，全局唯一
icon: 🔧
group: 数据分析         # 侧边栏分组
description: 一句话说清它做什么
schema: form.yaml
```

`form.yaml` 声明输入输出，`logic.py` 里写一个函数收 `params`、返回 `dict`：

```python
def analyze(params):
    return {"metrics": {...}, "summary": df, "fig": fig, "csv": bytes}
```

表单提交后，平台会：上传文件先落盘 → 调 `logic.py` → 结果存进 `session_state`（切页回来不丢）→ 按 `outputs` 渲染 → 记一条运行历史。

## 怎么做到的

**`core/registry.py`** 扫描 `tools/` 下每个目录，读 `meta.yaml`，按 `url` / `schema` / `entry` 决定用哪个渲染器。加载失败的工具不会中断启动，只记进 `LOAD_ERRORS`，首页统一展示。所有 `slug` 必须唯一，重复直接抛错——早失败比晚失败便宜。

**`core/schema_runner.py`** 把 `form.yaml` 的 `inputs` 变成 Streamlit 表单。关键一步是把 `UploadedFile` 转成普通 dict（含 `path`），`logic.py` 因此完全不接触 Streamlit 对象，可以单独测。结果放 `session_state` 而不是局部变量，是为了切页回来还在。

**`core/store.py`** 是唯一的持久化入口，工具里不允许直接写文件或连库。SQLite 开 WAL（多会话并发读），建表用 `CREATE TABLE IF NOT EXISTS`，所以部署不需要迁移步骤；上传、导出、`settings.json` 都放在 `DATA_DIR` 下，和代码分离。

## 边界

- **单进程 Streamlit**：没有用户体系，也没有并发控制。多人同时用会看到彼此的 `session_state`。
- **SQLite 够单机**：真上量，瓶颈会先出现在 Streamlit 而不是库。
- **插件之间无约束**：没有依赖声明、没有权限隔离、没有版本校验。
- **没有测试**：`logic.py` 是纯函数、容易测，但这套代码本身没写。

## License

[MIT](LICENSE)
