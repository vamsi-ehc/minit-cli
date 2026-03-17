"""Thread-safe rolling 10-minute stats store.

Snapshots are collected every ``INTERVAL`` seconds.  Only the last
``WINDOW_SECONDS / INTERVAL`` snapshots are kept, giving a 10-minute
sliding window.
"""

from __future__ import annotations

import datetime
import threading
from collections import deque
from typing import Deque, Dict, Any

WINDOW_SECONDS: int = 600   # 10 minutes
INTERVAL: int = 10           # collect every 10 s  → 60 snapshots


class StatsStore:
    """Thread-safe circular buffer of machine-stats snapshots."""

    def __init__(
        self,
        window_seconds: int = WINDOW_SECONDS,
        interval: int = INTERVAL,
    ) -> None:
        max_len = max(1, window_seconds // interval)
        self._buf: Deque[Dict[str, Any]] = deque(maxlen=max_len)
        self._lock = threading.Lock()

    def push(self, snapshot: Dict[str, Any]) -> None:
        """Append a snapshot (thread-safe)."""
        with self._lock:
            self._buf.append(snapshot)

    def all(self) -> list:
        """Return a shallow copy of all stored snapshots."""
        with self._lock:
            return list(self._buf)

    def __len__(self) -> int:
        with self._lock:
            return len(self._buf)


# Module-level singleton shared between the background collector thread
# and the FastAPI application.
store = StatsStore()
