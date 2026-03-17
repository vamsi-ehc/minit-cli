"""Memory utilization statistics."""

from __future__ import annotations

import psutil


def _bytes_to_mb(value: int) -> float:
    return round(value / (1024 ** 2), 1)


def collect() -> dict:
    """Return a snapshot of virtual and swap memory.

    Returns
    -------
    dict with keys:
        ``virtual``  – virtual (RAM) stats dict
        ``swap``     – swap stats dict
    """
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()

    return {
        "virtual": {
            "total_mb": _bytes_to_mb(vm.total),
            "available_mb": _bytes_to_mb(vm.available),
            "used_mb": _bytes_to_mb(vm.used),
            "percent": vm.percent,
        },
        "swap": {
            "total_mb": _bytes_to_mb(sw.total),
            "used_mb": _bytes_to_mb(sw.used),
            "free_mb": _bytes_to_mb(sw.free),
            "percent": sw.percent,
        },
    }
