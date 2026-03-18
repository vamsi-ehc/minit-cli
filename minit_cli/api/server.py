"""FastAPI application exposing last-10-minute stats as JSON.

Endpoints
---------
GET /stats        – return all snapshots collected in the last 10 minutes
GET /stats/latest – return only the most-recent snapshot
GET /health       – liveness probe
"""

from __future__ import annotations

import datetime
import threading
import time
from typing import Any, Dict, List

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

from minit_cli.api.store import store, INTERVAL
from minit_cli.collectors import cpu, memory, disk, network, processes, sysinfo

_collector_thread: threading.Thread | None = None
_stop_event = threading.Event()


# ---------------------------------------------------------------------------
# Background collector
# ---------------------------------------------------------------------------

def _collect_once() -> Dict[str, Any]:
    return {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cpu": cpu.collect(),
        "memory": memory.collect(),
        "disk": disk.collect(),
        "network": network.collect(),
        "processes": processes.collect(),
    }


def _collector_loop(stop: threading.Event, interval: int) -> None:
    # Prime psutil CPU percent (first call always returns 0.0)
    import psutil
    psutil.cpu_percent(interval=None, percpu=True)
    while not stop.is_set():
        snapshot = _collect_once()
        store.push(snapshot)
        stop.wait(interval)


def start_collector(interval: int = INTERVAL) -> None:
    """Start the background stats collector (idempotent)."""
    global _collector_thread
    if _collector_thread is not None and _collector_thread.is_alive():
        return
    _stop_event.clear()
    _collector_thread = threading.Thread(
        target=_collector_loop,
        args=(_stop_event, interval),
        daemon=True,
        name="minit-collector",
    )
    _collector_thread.start()


def stop_collector() -> None:
    """Signal the background collector to stop."""
    _stop_event.set()


# ---------------------------------------------------------------------------
# FastAPI lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(application: FastAPI):  # pragma: no cover
    start_collector()
    yield
    stop_collector()


app = FastAPI(
    title="minit-cli stats API",
    description="Export last 10 minutes of machine statistics as JSON.",
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    """Serve the real-time web dashboard."""
    from minit_cli.dashboard.web import HTML
    return HTML


@app.get("/sysinfo", response_class=JSONResponse)
def get_sysinfo() -> Dict[str, Any]:
    """Return static system information (hostname, OS, CPU, RAM, boot time)."""
    return sysinfo.collect()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/stats", response_class=JSONResponse)
def get_stats() -> List[Dict[str, Any]]:
    """Return all snapshots from the last 10 minutes."""
    return store.all()


@app.get("/stats/latest", response_class=JSONResponse)
def get_latest() -> Dict[str, Any]:
    """Return the most recent snapshot."""
    snapshots = store.all()
    if not snapshots:
        raise HTTPException(status_code=503, detail="No data collected yet.")
    return snapshots[-1]
