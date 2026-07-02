"""
database.py
-------------
SQLite persistence layer for FraudShield AI.

Stores every analyzed message + AI result in fraudshield.db so the
platform keeps a history / audit trail (useful for a demo dashboard
or future analytics).
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fraudshield.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT NOT NULL,
            prediction TEXT NOT NULL,
            fraud_type TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def log_message(message, prediction, fraud_type, confidence, risk_score, risk_level):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chat_history (message, prediction, fraud_type, confidence, risk_score, risk_level, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (message, prediction, fraud_type, confidence, risk_score, risk_level, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(limit=50):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chat_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM chat_history")
    total = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS scams FROM chat_history WHERE prediction='Scam'")
    scams = cur.fetchone()["scams"]
    conn.close()
    return {"total": total, "scams": scams, "safe": total - scams}