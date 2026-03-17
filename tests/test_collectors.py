"""Tests for the stats collectors."""

from __future__ import annotations

import time
import psutil
import pytest

from minit_cli.collectors import cpu, memory, disk, network, processes


# ---------------------------------------------------------------------------
# CPU
# ---------------------------------------------------------------------------

class TestCpuCollector:
    def test_keys_present(self):
        # Prime psutil
        psutil.cpu_percent(interval=None, percpu=True)
        time.sleep(0.1)
        data = cpu.collect()
        assert "per_core_percent" in data
        assert "overall_percent" in data
        assert "count_logical" in data
        assert "count_physical" in data
        assert "freq_mhz" in data

    def test_per_core_list_length(self):
        psutil.cpu_percent(interval=None, percpu=True)
        time.sleep(0.1)
        data = cpu.collect()
        assert len(data["per_core_percent"]) >= 1

    def test_overall_in_range(self):
        psutil.cpu_percent(interval=None, percpu=True)
        time.sleep(0.1)
        data = cpu.collect()
        assert 0.0 <= data["overall_percent"] <= 100.0

    def test_core_values_in_range(self):
        psutil.cpu_percent(interval=None, percpu=True)
        time.sleep(0.1)
        data = cpu.collect()
        for pct in data["per_core_percent"]:
            assert 0.0 <= pct <= 100.0

    def test_count_logical_positive(self):
        data = cpu.collect()
        assert data["count_logical"] >= 1


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

class TestMemoryCollector:
    def test_keys_present(self):
        data = memory.collect()
        assert "virtual" in data
        assert "swap" in data

    def test_virtual_keys(self):
        data = memory.collect()
        vm = data["virtual"]
        for key in ("total_mb", "available_mb", "used_mb", "percent"):
            assert key in vm, f"Missing key: {key}"

    def test_virtual_percent_in_range(self):
        data = memory.collect()
        assert 0.0 <= data["virtual"]["percent"] <= 100.0

    def test_virtual_total_positive(self):
        data = memory.collect()
        assert data["virtual"]["total_mb"] > 0


# ---------------------------------------------------------------------------
# Disk
# ---------------------------------------------------------------------------

class TestDiskCollector:
    def test_keys_present(self):
        data = disk.collect()
        assert "partitions" in data
        assert "io" in data

    def test_partitions_not_empty(self):
        data = disk.collect()
        assert len(data["partitions"]) >= 1

    def test_partition_keys(self):
        data = disk.collect()
        for part in data["partitions"]:
            for key in ("device", "mountpoint", "fstype", "total_gb", "used_gb", "free_gb", "percent"):
                assert key in part, f"Missing key: {key}"

    def test_partition_percent_in_range(self):
        data = disk.collect()
        for part in data["partitions"]:
            assert 0.0 <= part["percent"] <= 100.0


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

class TestNetworkCollector:
    def test_keys_present(self):
        data = network.collect()
        assert "interfaces" in data

    def test_interface_keys(self):
        data = network.collect()
        for nic, stats in data["interfaces"].items():
            for key in ("bytes_sent_mb", "bytes_recv_mb", "packets_sent", "packets_recv"):
                assert key in stats, f"NIC {nic} missing key: {key}"


# ---------------------------------------------------------------------------
# Processes
# ---------------------------------------------------------------------------

class TestProcessCollector:
    def test_keys_present(self):
        data = processes.collect()
        assert "processes" in data

    def test_returns_list(self):
        data = processes.collect()
        assert isinstance(data["processes"], list)

    def test_respects_limit(self):
        data = processes.collect(limit=5)
        assert len(data["processes"]) <= 5

    def test_process_keys(self):
        data = processes.collect(limit=1)
        if data["processes"]:
            proc = data["processes"][0]
            for key in ("pid", "name", "username", "status", "cpu_percent", "memory_percent"):
                assert key in proc, f"Missing key: {key}"

    def test_sorted_by_cpu_desc(self):
        data = processes.collect(limit=20)
        procs = data["processes"]
        for i in range(len(procs) - 1):
            assert procs[i]["cpu_percent"] >= procs[i + 1]["cpu_percent"]
