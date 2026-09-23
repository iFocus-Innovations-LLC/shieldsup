"""Append-only HITL audit log. Insert and read only."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.config import audit_db_path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS hitl_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    model_id TEXT NOT NULL,
    approx_tokens INTEGER NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('approve', 'deny')),
    token_mode TEXT NOT NULL CHECK (token_mode IN ('byok', 'pool'))
);

CREATE TRIGGER IF NOT EXISTS hitl_events_no_update
BEFORE UPDATE ON hitl_events
BEGIN
    SELECT RAISE(ABORT, 'hitl_events is append-only');
END;

CREATE TRIGGER IF NOT EXISTS hitl_events_no_delete
BEFORE DELETE ON hitl_events
BEGIN
    SELECT RAISE(ABORT, 'hitl_events is append-only');
END;
"""


def connect() -> sqlite3.Connection:
    path = audit_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    return conn


def insert_event(
    *,
    tenant_id: str,
    actor: str,
    action: str,
    model_id: str,
    approx_tokens: int,
    decision: str,
    token_mode: str,
) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO hitl_events (
                tenant_id, actor, action, timestamp, model_id,
                approx_tokens, decision, token_mode
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tenant_id,
                actor,
                action,
                timestamp,
                model_id,
                approx_tokens,
                decision,
                token_mode,
            ),
        )
        event_id = cursor.lastrowid
    return get_event(event_id)


def get_event(event_id: int) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM hitl_events WHERE id = ?",
            (event_id,),
        ).fetchone()
    if row is None:
        raise KeyError(event_id)
    return _row_to_dict(row)


def list_events(*, tenant_id: str | None, limit: int) -> list[dict[str, Any]]:
    query = "SELECT * FROM hitl_events"
    params: list[Any] = []
    if tenant_id is not None:
        query += " WHERE tenant_id = ?"
        params.append(tenant_id)
    query += " ORDER BY id ASC LIMIT ?"
    params.append(limit)
    with connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_dict(row) for row in rows]


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["remediation_executed"] = False
    return item
