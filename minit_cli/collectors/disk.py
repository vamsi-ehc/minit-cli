"""Disk space and disk I/O statistics."""

from __future__ import annotations

import psutil

# Pseudo / in-memory / virtual filesystems that are not real storage.
_VIRTUAL_FS: frozenset[str] = frozenset({
    "squashfs", "tmpfs", "devtmpfs", "devfs", "sysfs", "proc", "procfs",
    "cgroup", "cgroup2", "cgroupfs", "fusectl", "securityfs", "pstorefs",
    "debugfs", "tracefs", "configfs", "overlay", "aufs", "iso9660", "udf",
    "ramfs", "rootfs", "bpf", "mqueue", "hugetlbfs", "efivarfs", "pstore",
    "fuse.portal", "fuse.gvfsd-fuse", "fuse.snapfuse", "nsfs", "rpc_pipefs",
    "nfsd", "sunrpc",
})


def _bytes_to_gb(value: int) -> float:
    return round(value / (1024 ** 3), 2)


def _bytes_to_mb(value: int) -> float:
    return round(value / (1024 ** 2), 1)


def _is_real_mount(part) -> bool:
    """Return True for user-visible, real-storage mount points."""
    if part.fstype.lower() in _VIRTUAL_FS:
        return False
    # Skip kernel loop devices (snap packages, etc.)
    if part.device.startswith("/dev/loop"):
        return False
    return True


def collect() -> dict:
    """Return a snapshot of disk space and I/O counters.

    Returns
    -------
    dict with keys:
        ``partitions`` – list of real mounted partition dicts (space usage)
        ``io``         – dict of per-disk I/O counters (may be empty on some VMs)
    """
    partitions = []
    for part in psutil.disk_partitions(all=False):
        if not _is_real_mount(part):
            continue
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
