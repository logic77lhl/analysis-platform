[中文](README.md) | **English**

# Analysis Platform

A Streamlit container for analysis tools: drop a directory into `tools/`, write a `meta.yaml`, and it appears in the sidebar and on the home page. `app.py` never changes.

It performs no analysis itself. It solves the problem of what analysis scripts become once there are many of them — scattered notebooks, parameters hard-coded, every new dataset meaning another edit.

## What it provides

Four things, and nothing else:

- **Registration** — scans `tools/`, reads `meta.yaml`, builds navigation and home cards
- **Parameter UI** — inputs declared in `form.yaml`, form rendered automatically
- **Persistence** — uploads, run history, and settings all go through `core/store.py`
- **Result rendering** — metric cards, tables, Plotly charts, downloads, driven by `outputs`

## Three ways to plug in

| Mode | What you write | Good for |
|---|---|---|
| **schema-driven** | `meta.yaml` + `form.yaml` + `logic.py` | simple inputs, fixed outputs; zero UI code |
| **free render** | `meta.yaml` (`entry: render`) + your own `render()` | complex, multi-step interactions |
| **external link** | `url` in `meta.yaml` | services running elsewhere; the platform just links out |

## Usage

```bash
pip install -r requirements.txt
streamlit run app.py
```

Data defaults to `./data`. In deployment, point `DATA_DIR` at a mounted volume so redeploys don't lose data:

```bash
DATA_DIR=/data streamlit run app.py
```

Three tools ship with it: **Data overview** (upload CSV/Excel → summary, metric cards, distribution of the first numeric column), **Text analysis** (character counts and top-N word frequency, Chinese and English), and **Settings** (writes to `DATA_DIR/settings.json`).

## Adding a tool

Minimal shape (schema-driven):

```
tools/my_tool/
├── meta.yaml
├── form.yaml
└── logic.py
```

`meta.yaml`:

```yaml
name: My Tool
slug: my-tool          # URL id, globally unique
icon: 🔧
group: Data analysis   # sidebar group
description: One line on what it does
schema: form.yaml
```

`form.yaml` declares inputs and outputs; `logic.py` exposes one function that takes `params` and returns a dict:

```python
def analyze(params):
    return {"metrics": {...}, "summary": df, "fig": fig, "csv": bytes}
```

On submit the platform: saves uploaded files to disk → calls `logic.py` → stores results in `session_state` (survive page switches) → renders according to `outputs` → records a run.

## How it works

**`core/registry.py`** walks `tools/`, reads each `meta.yaml`, and picks a renderer from `url` / `schema` / `entry`. A tool that fails to load doesn't take the platform down — the error goes into `LOAD_ERRORS` and shows on the home page. Slugs must be unique; duplicates raise immediately, because failing early is cheaper than failing late.

**`core/schema_runner.py`** turns `form.yaml` inputs into a Streamlit form. The key move is converting `UploadedFile` into a plain dict (including a `path`), so `logic.py` never touches Streamlit objects and can be tested on its own. Results go into `session_state` rather than a local variable so they survive navigation.

**`core/store.py`** is the only persistence entry point; tools may not write files or open databases directly. SQLite runs in WAL mode (concurrent reads), tables are created with `CREATE TABLE IF NOT EXISTS` so deployment needs no migration step, and uploads/exports/`settings.json` live under `DATA_DIR`, separate from code.

## Limits

- **Single-process Streamlit**: no user accounts, no concurrency control. Multiple people at once will see each other's `session_state`.
- **SQLite is a single-machine choice**: at real scale, Streamlit becomes the bottleneck before the database does.
- **No constraints between plugins**: no dependency declarations, no permission isolation, no version checks.
- **No tests**: `logic.py` is a pure function and easy to test, but this codebase doesn't test it.

## License

[MIT](LICENSE)
