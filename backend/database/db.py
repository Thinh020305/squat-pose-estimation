from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    name TEXT NOT NULL,
    goal TEXT,
    password_hash TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS workout_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TEXT,
    total_reps INTEGER NOT NULL DEFAULT 0,
    average_score REAL NOT NULL DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS squat_reps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    rep_number INTEGER NOT NULL,
    min_knee_angle REAL NOT NULL,
    max_torso_lean REAL NOT NULL,
    duration_seconds REAL NOT NULL,
    depth_score INTEGER NOT NULL,
    torso_score INTEGER NOT NULL,
    tempo_score INTEGER NOT NULL,
    total_score INTEGER NOT NULL,
    feedback TEXT NOT NULL,
    label TEXT,
    confidence REAL NOT NULL DEFAULT 0,
    evaluator TEXT NOT NULL DEFAULT 'rule_based',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES workout_sessions(id)
);
CREATE TABLE IF NOT EXISTS training_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    scheduled_date TEXT NOT NULL,
    workout_name TEXT NOT NULL,
    target_reps INTEGER,
    note TEXT,
    completed INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
"""


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        db_path = Path(current_app.config["DATABASE"])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_database(app) -> None:
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.executescript(SCHEMA)
    connection.commit()
    connection.close()
    app.teardown_appcontext(close_db)
