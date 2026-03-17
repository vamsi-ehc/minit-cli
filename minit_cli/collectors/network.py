"""Network interface statistics."""

from __future__ import annotations

import psutil


def _bytes_to_mb(value: int) -> float:
    return round(value / (1024 ** 2), 2)


def collect() -> dict:
    """Return a snapshot of per-NIC network I/O counters.

    Returns
    -------
    dict with keys:
        ``interfaces`` – dict keyed by NIC name, each value is a stats dict
    """
    counters = psutil.net_io_counters(pernic=True) or {}
    interfaces = {}
    for nic, stats in counters.items():
        interfaces[nic] = {
            "bytes_sent_mb": _bytes_to_mb(stats.bytes_sent),
            "bytes_recv_mb": _bytes_to_mb(stats.bytes_recv),
            "packets_sent": stats.packets_sent,
            "packets_recv": stats.packets_recv,
            "errin": stats.errin,
            "errout": stats.errout,
            "dropin": stats.dropin,
            "dropout": stats.dropout,
        }
    return {"interfaces": interfaces}
