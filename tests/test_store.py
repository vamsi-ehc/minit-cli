"""Tests for the rolling stats store."""

from __future__ import annotations

import time

import pytest

from minit_cli.api.store import StatsStore


class TestStatsStore:
    def test_empty_on_init(self):
        s = StatsStore()
        assert len(s) == 0
        assert s.all() == []

    def test_push_and_retrieve(self):
        s = StatsStore()
        s.push({"a": 1})
        assert len(s) == 1
        assert s.all() == [{"a": 1}]

    def test_maxlen_respected(self):
        s = StatsStore(window_seconds=10, interval=5)  # maxlen = 2
        for i in range(5):
            s.push({"i": i})
        assert len(s) == 2
        snapshots = s.all()
        # Only the last 2 items should be kept
        assert snapshots[-1] == {"i": 4}
        assert snapshots[-2] == {"i": 3}

    def test_all_returns_copy(self):
        s = StatsStore()
        s.push({"x": 1})
        copy1 = s.all()
        copy2 = s.all()
        assert copy1 is not copy2

    def test_thread_safety(self):
        """Push from multiple threads; verify count stays within maxlen."""
        import threading

        window, interval = 60, 5  # maxlen = 12
        s = StatsStore(window_seconds=window, interval=interval)

        def _push(n):
            for i in range(n):
                s.push({"v": i})

        threads = [threading.Thread(target=_push, args=(50,)) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(s) <= window // interval
