"""Tests for the FastAPI stats server."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from minit_cli.api.server import app
from minit_cli.api.store import store


@pytest.fixture(autouse=True)
def _clear_store():
    """Ensure a clean store before each test."""
    store._buf.clear()
    yield
    store._buf.clear()


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_ok(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestStatsEndpoint:
    def test_empty_returns_list(self):
        resp = client.get("/stats")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_pushed_snapshots(self):
        store.push({"ts": "t1", "cpu": {}})
        store.push({"ts": "t2", "cpu": {}})
        resp = client.get("/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["ts"] == "t1"
        assert data[1]["ts"] == "t2"


class TestStatsLatestEndpoint:
    def test_503_when_empty(self):
        resp = client.get("/stats/latest")
        assert resp.status_code == 503

    def test_returns_last_snapshot(self):
        store.push({"ts": "old"})
        store.push({"ts": "new"})
        resp = client.get("/stats/latest")
        assert resp.status_code == 200
        assert resp.json()["ts"] == "new"
