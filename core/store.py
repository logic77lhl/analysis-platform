"""平台唯一持久化入口 —— 所有写操作必须走这里，禁止在工具里直写文件/数据库。

数据与代码分离：数据一律存 DATA_DIR（环境变量，默认 ./data）。
  - 本地开发：DATA_DIR 缺省 → 项目目录下 ./data
  - CI/CD 部署：-e DATA_DIR=/data 并挂载 volume，重新发版数据不丢

目录布局：
  $DATA_DIR/
  ├── app.db          # SQLite 业务数据（建表幂等，部署时无需迁移步骤）
  ├── uploads/        # 用户上传的文件
  ├── exports/        # 导出文件
  └── settings.json   # 用户配置（系统设置页写入）
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import uuid
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))
UPLOADS = DATA_DIR / "uploads"
EXPORTS = DATA_DIR / "exports"
SETTINGS_FILE = DATA_DIR / "settings.json"
DB_FILE = DATA_DIR / "app.db"

_conn: sqlite3.Connection | None = None
_lock = threading.Lock()


def init() -> None:
    """确保目录与数据表存在（幂等，可反复调用）。"""
    get_conn()


def get_conn() -> sqlite3.Connection:
    """SQLite 连接单例（WAL 模式，支持多会话并发读）。"""
    global _conn
    if _conn is None:
        with _lock:
            if _conn is None:
                for d in (DATA_DIR, UPLOADS, EXPORTS):
                    d.mkdir(parents=True, exist_ok=True)
                c = sqlite3.connect(DB_FILE, check_same_thread=False)
                c.row_factory = sqlite3.Row
                c.execute("PRAGMA journal_mode=WAL")
                c.execute(
                    "CREATE TABLE IF NOT EXISTS run_history ("
                    " id INTEGER PRIMARY KEY AUTOINCREMENT,"
                    " tool TEXT NOT NULL,"
                    " payload TEXT NOT NULL,"   # JSON
                    " created_at TEXT NOT NULL)"
                )
                c.commit()
                _conn = c
    return _conn


# ── 业务数据（SQLite） ──────────────────────────────

def record_run(tool: str, payload: dict) -> None:
    """记录一次工具运行，payload 以 JSON 存储。"""
    with _lock:
        get_conn().execute(
            "INSERT INTO run_history (tool, payload, created_at) VALUES (?, ?, ?)",
            (tool, json.dumps(payload, ensure_ascii=False),
             datetime.now().isoformat(timespec="seconds")),
        )
        get_conn().commit()


def list_runs(tool: str | None = None, limit: int = 10) -> list[dict]:
    """最近运行记录，payload 已解析为 dict，按时间倒序。"""
    q = "SELECT tool, payload, created_at FROM run_history"
    args: tuple = ()
    if tool:
        q += " WHERE tool = ?"
        args = (tool,)
    q += " ORDER BY id DESC LIMIT ?"
    args += (limit,)
    rows = get_conn().execute(q, args).fetchall()
    return [{"tool": r["tool"],
             "payload": json.loads(r["payload"]),
             "created_at": r["created_at"]} for r in rows]


# ── 用户配置（settings.json） ────────────────────────

def load_settings() -> dict:
    if SETTINGS_FILE.is_file():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_settings(settings: dict) -> None:
    """原子写入，避免写一半被读到残缺 JSON。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(settings, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(SETTINGS_FILE)


# ── 文件存储（uploads / exports） ────────────────────

def save_upload(name: str, data: bytes) -> Path:
    """保存上传文件，返回落盘路径。文件名加时间戳与随机后缀防覆盖。"""
    UPLOADS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = re.sub(r'[\\/:*?"<>|]', "_", name)
    path = UPLOADS / f"{stamp}-{uuid.uuid4().hex[:4]}__{safe}"
    path.write_bytes(data)
    return path
