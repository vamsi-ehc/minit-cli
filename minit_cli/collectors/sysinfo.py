"""System-level information (hostname, OS, CPU model, RAM, boot time)."""

from __future__ import annotations

import datetime
import platform
import socket

import psutil


def collect() -> dict:
    """Return static / slow-changing system information."""
    uname = platform.uname()
    boot_ts = psutil.boot_time()
    boot_dt = datetime.datetime.fromtimestamp(boot_ts, datetime.timezone.utc)
    uptime_s = int(
        (datetime.datetime.now(datetime.timezone.utc) - boot_dt).total_seconds()
    )
    vm = psutil.virtual_memory()

    return {
        "hostname": socket.gethostname(),
        "os": f"{uname.system} {uname.release}",
        "machine": uname.machine,
        "processor": uname.processor or uname.machine,
        "logical_cores": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
        "total_ram_gb": round(vm.total / (1024 ** 3), 2),
        "boot_time": boot_dt.isoformat(),
        "uptime_seconds": uptime_s,
    }
