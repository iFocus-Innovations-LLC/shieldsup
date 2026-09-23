"""Runtime settings. Read on each call so tests can change the environment."""

from __future__ import annotations

import os
from pathlib import Path

TOKEN_MODES = frozenset({"byok", "pool"})


class ConfigError(ValueError):
    """Raised when TOKEN_MODE or POOL_REMAINING is unusable."""


def token_mode() -> str:
    mode = os.environ.get("TOKEN_MODE", "byok").strip().lower()
    if mode not in TOKEN_MODES:
        raise ConfigError("TOKEN_MODE must be byok or pool")
    return mode


def pool_remaining() -> int:
    raw = os.environ.get("POOL_REMAINING", "10000").strip()
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigError("POOL_REMAINING must be an integer") from exc
    if value < 0:
        raise ConfigError("POOL_REMAINING must be >= 0")
    return value


def audit_db_path() -> Path:
    return Path(os.environ.get("AUDIT_DB_PATH", "data/audit.db"))
