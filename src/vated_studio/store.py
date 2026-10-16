from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class StudioStore:
    """SQLite state with short-lived connections and explicit transactions."""
    def __init__(self, workspace: Path):
        self.path = workspace / ".state" / "studio.sqlite3"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=20)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute("PRAGMA busy_timeout=20000")
        return connection

    def _init(self) -> None:
        with self.connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY, project_id TEXT, kind TEXT NOT NULL, relative_path TEXT NOT NULL,
                sha256 TEXT NOT NULL, metadata_json TEXT NOT NULL, created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY, command TEXT NOT NULL, status TEXT NOT NULL,
                started_at REAL NOT NULL, finished_at REAL, request_json TEXT NOT NULL,
                result_json TEXT, error_json TEXT
            );
            CREATE TABLE IF NOT EXISTS events (
                seq INTEGER PRIMARY KEY AUTOINCREMENT, created_at REAL NOT NULL,
                kind TEXT NOT NULL, payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY, project_id TEXT, artifact_id TEXT, category TEXT NOT NULL,
                rating INTEGER, notes TEXT NOT NULL, reviewer_type TEXT NOT NULL,
                created_at REAL NOT NULL, context_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_runs_started ON runs(started_at DESC);
            CREATE INDEX IF NOT EXISTS idx_assets_project ON assets(project_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at DESC);
            """)

    def start_run(self, run_id: str, command: str, payload: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO runs(id,command,status,started_at,request_json) VALUES(?,?,?,?,?)",
                       (run_id, command, "running", time.time(), json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)))
        self.event("run_started", {"run_id": run_id, "command": command})

    def finish_run(self, run_id: str, status: str, *, result: Any = None, error: Any = None) -> None:
        with self.connect() as db:
            db.execute("UPDATE runs SET status=?,finished_at=?,result_json=?,error_json=? WHERE id=?",
                       (status, time.time(), json.dumps(result, ensure_ascii=False, default=str) if result is not None else None,
                        json.dumps(error, ensure_ascii=False, default=str) if error is not None else None, run_id))
        self.event("run_finished", {"run_id": run_id, "status": status, "error": error})

    def event(self, kind: str, payload: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO events(created_at,kind,payload_json) VALUES(?,?,?)",
                       (time.time(), kind, json.dumps(payload, ensure_ascii=False, default=str)))

    def runs(self, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(500, int(limit)))
        with self.connect() as db:
            rows = db.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)).fetchall()
        return [{"id": r["id"], "command": r["command"], "status": r["status"],
                 "started_at": r["started_at"], "finished_at": r["finished_at"],
                 "request": json.loads(r["request_json"]),
                 "result": json.loads(r["result_json"]) if r["result_json"] else None,
                 "error": json.loads(r["error_json"]) if r["error_json"] else None} for r in rows]

    def record_asset(self, *, asset_id: str, project_id: str | None, kind: str, relative_path: str,
                     sha256: str, metadata: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO assets(id,project_id,kind,relative_path,sha256,metadata_json,created_at) VALUES(?,?,?,?,?,?,?)",
                       (asset_id, project_id, kind, relative_path, sha256, json.dumps(metadata, ensure_ascii=False, default=str), time.time()))
        self.event("asset_registered", {"asset_id": asset_id, "kind": kind, "path": relative_path, "sha256": sha256})

    def assets(self, limit: int = 100) -> list[dict[str, Any]]:
        limit = max(1, min(1000, int(limit)))
        with self.connect() as db:
            rows = db.execute("SELECT * FROM assets ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [{"id": r["id"], "project_id": r["project_id"], "kind": r["kind"],
                 "relative_path": r["relative_path"], "sha256": r["sha256"],
                 "metadata": json.loads(r["metadata_json"]), "created_at": r["created_at"]} for r in rows]

    def add_feedback(self, *, feedback_id: str, project_id: str | None, artifact_id: str | None,
                     category: str, rating: int | None, notes: str, reviewer_type: str,
                     context: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("INSERT INTO feedback(id,project_id,artifact_id,category,rating,notes,reviewer_type,created_at,context_json) VALUES(?,?,?,?,?,?,?,?,?)",
                       (feedback_id, project_id, artifact_id, category, rating, notes, reviewer_type, time.time(), json.dumps(context, ensure_ascii=False)))
        self.event("feedback_added", {"feedback_id": feedback_id, "category": category, "reviewer_type": reviewer_type})

    def counts(self) -> dict[str, int]:
        with self.connect() as db:
            return {table: int(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]) for table in ("assets", "runs", "events", "feedback")}
