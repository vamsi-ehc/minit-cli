"""stdlib HTTP server exposing last-N-minute stats as JSON.

Endpoints
---------
GET /             – real-time web dashboard (HTML)
GET /sysinfo      – static system information (hostname, OS, CPU, RAM, boot time)
GET /health       – liveness probe
GET /stats        – return all snapshots in the rolling window
GET /stats/latest – return only the most-recent snapshot
"""

from __future__ import annotations

import datetime
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from minit_cli.api.store import store, INTERVAL
from minit_cli.collectors import cpu, memory, disk, network, processes, sysinfo, users

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
        "users": users.collect(),
    }


def _collector_loop(
    stop: threading.Event,
    interval: int,
    store: StatsStore,
    log_dir: str,
    thresholds: Dict[str, Any],
) -> None:
    import psutil
    from minit_cli import metrics_log

    psutil.cpu_percent(interval=None, percpu=True)
    while not stop.is_set():
        try:
            snapshot = _collect_once()
            store.push(snapshot)
            metrics_log.write_snapshot(snapshot, log_dir)
            metrics_log.check_thresholds(snapshot, thresholds, log_dir)
        except Exception as exc:  # noqa: BLE001
            import traceback
            traceback.print_exc()
        stop.wait(interval)


def start_collector(
    interval: int,
    store: StatsStore,
    log_dir: str,
    thresholds: Dict[str, Any],
) -> None:
    """Start the background stats collector (idempotent)."""
    global _collector_thread
    if _collector_thread is not None and _collector_thread.is_alive():
        return
    _stop_event.clear()
    _collector_thread = threading.Thread(
        target=_collector_loop,
        args=(_stop_event, interval, store, log_dir, thresholds),
        daemon=True,
        name="minit-collector",
    )
    _collector_thread.start()


def stop_collector() -> None:
    """Signal the background collector to stop."""
    _stop_event.set()


# ---------------------------------------------------------------------------
# HTTP handler factory
# ---------------------------------------------------------------------------

def _make_handler(store: StatsStore):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, format: str, *args: Any) -> None:
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

    return _Handler


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    interval: int = INTERVAL,
    window_seconds: int = WINDOW_SECONDS,
) -> None:
    """Start the HTTP server (blocking).

    Reads log_path, retention_days, and thresholds from the config file.
    """
    from minit_cli import config as cfg_mod, metrics_log

    cfg = cfg_mod.load()
    log_dir: str = cfg["logging"]["log_path"]
    retention_days: int = cfg["logging"]["retention_days"]
    thresholds: Dict[str, Any] = cfg.get("thresholds", {})

    # Rotate stale log files on startup.
    metrics_log.rotate_logs(log_dir, retention_days)

    store = StatsStore(window_seconds=window_seconds, interval=interval)
    start_collector(interval=interval, store=store, log_dir=log_dir, thresholds=thresholds)

    server = HTTPServer((host, port), _make_handler(store))
    try:
        server.serve_forever()
    finally:
        stop_collector()
