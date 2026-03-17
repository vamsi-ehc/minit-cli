"""Per-core CPU statistics."""

from __future__ import annotations

from typing import List

import psutil


def collect() -> dict:
    """Return a snapshot of CPU statistics.

    Returns
    -------
    dict with keys:
        ``per_core_percent`` – list of per-logical-CPU utilization (0-100 %)
        ``overall_percent``  – overall utilization average across all cores
        ``count_logical``    – number of logical CPUs
        ``count_physical``   – number of physical CPUs (may be None)
        ``freq_mhz``         – current frequency in MHz (may be None)
    """
    per_core: List[float] = psutil.cpu_percent(interval=None, percpu=True)
    overall: float = psutil.cpu_percent(interval=None)

    freq = psutil.cpu_freq()
    freq_mhz: float | None = round(freq.current, 1) if freq else None

    return {
        "per_core_percent": per_core,
        "overall_percent": overall,
        "count_logical": psutil.cpu_count(logical=True),
        "count_physical": psutil.cpu_count(logical=False),
        "freq_mhz": freq_mhz,
    }
