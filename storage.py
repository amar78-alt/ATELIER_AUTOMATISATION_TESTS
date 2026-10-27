"""Stockage SQLite des exécutions de tests."""

import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "runs.db"


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                api TEXT NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                error_rate REAL NOT NULL,
                latency_avg REAL,
                latency_p95 REAL,
                results_json TEXT NOT NULL
            )
        """)
        db.commit()


def save_run(timestamp, summary, results):
    init_db()
    with connect() as db:
        cursor = db.execute("""
            INSERT INTO runs
            (timestamp, api, passed, failed, error_rate, latency_avg, latency_p95, results_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp,
            "Frankfurter",
            summary["passed"],
            summary["failed"],
            summary["error_rate"],
            summary["latency_avg"],
            summary["latency_p95"],
            json.dumps(results, ensure_ascii=False),
        ))
        db.commit()
        return cursor.lastrowid


def list_runs(limit=50):
    init_db()
    with connect() as db:
        rows = db.execute(
            "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(row) for row in rows]


def get_run(run_id):
    init_db()
    with connect() as db:
        row = db.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    return dict(row) if row else None
