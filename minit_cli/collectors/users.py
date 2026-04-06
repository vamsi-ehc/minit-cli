"""Currently logged-in users."""

from __future__ import annotations

import datetime

import psutil


def collect() -> dict:
    """Return a list of currently logged-in users."""
    users = []
    for u in psutil.users():
        users.append(
            {
                "name": u.name,
                "terminal": u.terminal or "—",
                "host": u.host or "local",
                "started": datetime.datetime.fromtimestamp(u.started).strftime(
                    "%Y-%m-%d %H:%M"
                ),
            }
        )
    return {"users": users}
