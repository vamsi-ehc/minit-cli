"""Running process list."""

from __future__ import annotations

from typing import List

import psutil


_ATTRS = ["pid", "name", "username", "status", "cpu_percent", "memory_percent"]

_CPU_COUNT = max(psutil.cpu_count() or 1, 1)


def collect(limit: int = 50) -> dict:
    """Return up to *limit* processes (top by CPU and RAM combined pool).

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
        # Skip System Idle Process
        if (info["name"] or "").lower() == "system idle process":
            continue
        # Normalize cpu_percent to 0-100 range (psutil returns per-core %)
        raw_cpu = info["cpu_percent"] or 0.0
        procs.append(
            {
                "pid": info["pid"],
                "name": info["name"] or "",
                "username": info["username"] or "",
                "status": info["status"] or "",
                "cpu_percent": round(min(raw_cpu / _CPU_COUNT, 100.0), 1),
                "memory_percent": round(info["memory_percent"] or 0.0, 2),
            }
        )

    # Return a combined pool: top-25 by CPU + top-25 by RAM (deduped)
    by_cpu = sorted(procs, key=lambda p: p["cpu_percent"], reverse=True)[:25]
    by_ram = sorted(procs, key=lambda p: p["memory_percent"], reverse=True)[:25]
    seen: set = set()
    pool: List[dict] = []
    for p in by_cpu + by_ram:
        if p["pid"] not in seen:
            seen.add(p["pid"])
            pool.append(p)
    return {"processes": pool}
