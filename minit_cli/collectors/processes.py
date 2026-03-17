"""Running process list."""

from __future__ import annotations

from typing import List

import psutil


_ATTRS = ["pid", "name", "username", "status", "cpu_percent", "memory_percent"]


def collect(limit: int = 20) -> dict:
    """Return the top *limit* processes sorted by CPU usage.

    Returns
    -------
    dict with key:
        ``processes`` – list of process dicts
    """
    procs: List[dict] = []
    for proc in psutil.process_iter(_ATTRS):
        try:
            info = proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        procs.append(
            {
                "pid": info["pid"],
                "name": info["name"] or "",
                "username": info["username"] or "",
                "status": info["status"] or "",
                "cpu_percent": round(info["cpu_percent"] or 0.0, 1),
                "memory_percent": round(info["memory_percent"] or 0.0, 2),
            }
        )

    procs.sort(key=lambda p: p["cpu_percent"], reverse=True)
    return {"processes": procs[:limit]}
