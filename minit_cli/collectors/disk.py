"""Disk space and disk I/O statistics."""

from __future__ import annotations

import psutil


def _bytes_to_gb(value: int) -> float:
    return round(value / (1024 ** 3), 2)


def _bytes_to_mb(value: int) -> float:
    return round(value / (1024 ** 2), 1)


def collect() -> dict:
    """Return a snapshot of disk space and I/O counters.

    Returns
    -------
    dict with keys:
        ``partitions`` – list of per-partition dicts (space usage)
        ``io``         – dict of per-disk I/O counters (may be empty on some VMs)
    """
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
        except (PermissionError, OSError):
            continue
        partitions.append(
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": _bytes_to_gb(usage.total),
                "used_gb": _bytes_to_gb(usage.used),
                "free_gb": _bytes_to_gb(usage.free),
                "percent": usage.percent,
            }
        )

    io_raw = psutil.disk_io_counters(perdisk=True) or {}
    io = {}
    for disk, counters in io_raw.items():
        io[disk] = {
            "read_mb": _bytes_to_mb(counters.read_bytes),
            "write_mb": _bytes_to_mb(counters.write_bytes),
            "read_count": counters.read_count,
            "write_count": counters.write_count,
        }

    return {"partitions": partitions, "io": io}
