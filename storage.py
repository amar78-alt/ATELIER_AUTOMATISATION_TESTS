"""Persistance SQLite de l'historique des runs."""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get("ATELIER_DB_PATH", str(Path(__file__).with_name("runs.sqlite3")))


def _connect():
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with _connect() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api TEXT NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                error_rate REAL NOT NULL,
                availability REAL NOT NULL,
                latency_avg REAL NOT NULL,
                latency_p95 REAL NOT NULL,
                duration_ms REAL NOT NULL,
                payload_json TEXT NOT NULL
            )
        """)


def save_run(run: dict) -> int:
    init_db()
    summary = run["summary"]
    with _connect() as connection:
        cursor = connection.execute("""
            INSERT INTO runs (
                timestamp, api, passed, failed, error_rate, availability,
                latency_avg, latency_p95, duration_ms, payload_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run["timestamp"], run["api"], summary["passed"], summary["failed"],
            summary["error_rate"], summary["availability"],
            summary["latency_ms_avg"], summary["latency_ms_p95"],
            run["duration_ms"], json.dumps(run, ensure_ascii=False),
        ))
        return int(cursor.lastrowid)


def get_run(run_id: int) -> dict | None:
    init_db()
    with _connect() as connection:
        row = connection.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        return None
    data = json.loads(row["payload_json"])
    data["id"] = row["id"]
    return data


def list_runs(limit: int = 20) -> list[dict]:
    init_db()
    with _connect() as connection:
        rows = connection.execute(
            "SELECT id, timestamp, api, passed, failed, error_rate, availability, "
            "latency_avg, latency_p95, duration_ms FROM runs ORDER BY id DESC LIMIT ?",
            (max(1, min(int(limit), 100)),),
        ).fetchall()
    return [dict(row) for row in rows]
