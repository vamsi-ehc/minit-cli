"""stdlib HTTP server exposing last-10-minute stats as JSON.

Endpoints
---------
GET /             – real-time web dashboard (HTML)
GET /sysinfo      – static system information (hostname, OS, CPU, RAM, boot time)
GET /health       – liveness probe
GET /stats        – return all snapshots collected in the last 10 minutes
GET /stats/latest – return only the most-recent snapshot
"""

from __future__ import annotations

import datetime
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

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
# HTTP handler
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # silence request logs
        pass

    def _send_json(self, data: Any, status: int = 200) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str) -> None:
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = self.path.split("?")[0]
        if path == "/":
            from minit_cli.dashboard.web import HTML
            self._send_html(HTML)
        elif path == "/health":
            self._send_json({"status": "ok"})
        elif path == "/sysinfo":
            self._send_json(sysinfo.collect())
        elif path == "/stats":
            self._send_json(store.all())
        elif path == "/stats/latest":
            snapshots = store.all()
            if not snapshots:
                self._send_json({"detail": "No data collected yet."}, status=503)
            else:
                self._send_json(snapshots[-1])
        else:
            self._send_json({"detail": "Not found."}, status=404)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_server(host: str = "127.0.0.1", port: int = 8000, interval: int = INTERVAL) -> None:
    """Start the HTTP server (blocking). Runs the collector in a background thread."""
    start_collector(interval=interval)
    server = HTTPServer((host, port), _Handler)
    try:
        server.serve_forever()
    finally:
        stop_collector()
