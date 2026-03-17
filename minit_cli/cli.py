"""CLI entry point for minit-cli.

Usage
-----
  minit dashboard            # real-time terminal dashboard
  minit serve                # start the JSON export API server
  minit stats                # print a one-shot JSON snapshot to stdout
  minit stats --pretty       # pretty-print the JSON snapshot
  minit setup                # add minit to PATH (user + system)
"""

from __future__ import annotations

import json
import sys

import click

from minit_cli import __version__


@click.group()
@click.version_option(__version__, prog_name="minit")
def main() -> None:
    """minit-cli – real-time machine stats dashboard and export API."""


@main.command()
@click.option(
    "--refresh",
    default=2.0,
    show_default=True,
    type=float,
    help="Dashboard refresh interval in seconds.",
)
def dashboard(refresh: float) -> None:
    """Launch the real-time terminal dashboard.

    Press Ctrl+C to quit.
    """
    from minit_cli.dashboard.live import run

    run(refresh_interval=refresh)


@main.command()
@click.option("--host", default="127.0.0.1", show_default=True, help="Bind host.")
@click.option("--port", default=8000, show_default=True, help="Bind port.")
@click.option(
    "--interval",
    default=10,
    show_default=True,
    type=int,
    help="Stats collection interval in seconds.",
)
def serve(host: str, port: int, interval: int) -> None:
    """Start the JSON export API server.

    Collects stats every INTERVAL seconds and exposes them at:

    \b
      GET /stats         – last 10 minutes of snapshots
      GET /stats/latest  – most recent snapshot
      GET /health        – liveness probe
    """
    try:
        import uvicorn
    except ImportError:  # pragma: no cover
        click.echo("uvicorn is required: pip install 'minit-cli[serve]'", err=True)
        sys.exit(1)

    from minit_cli.api.server import app, start_collector
    from minit_cli.api.store import INTERVAL as DEFAULT_INTERVAL

    # Override the collection interval before starting the server.
    click.echo(
        f"Starting minit API server at http://{host}:{port}  "
        f"(collecting every {interval}s)"
    )
    start_collector(interval=interval)
    uvicorn.run(app, host=host, port=port, log_level="warning")


@main.command()
@click.option("--pretty", is_flag=True, default=False, help="Pretty-print JSON output.")
def stats(pretty: bool) -> None:
    """Print a one-shot JSON snapshot of all machine statistics to stdout."""
    import datetime
    import psutil

    from minit_cli.collectors import cpu, memory, disk, network, processes

    # Prime psutil (first call always returns 0.0)
    psutil.cpu_percent(interval=None, percpu=True)
    import time
    time.sleep(0.2)

    snapshot = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cpu": cpu.collect(),
        "memory": memory.collect(),
        "disk": disk.collect(),
        "network": network.collect(),
        "processes": processes.collect(),
    }
    indent = 2 if pretty else None
    click.echo(json.dumps(snapshot, indent=indent))


@main.command()
@click.option(
    "--system",
    is_flag=True,
    default=False,
    help="Also add to system-wide PATH (requires admin/root privileges).",
)
def setup(system: bool) -> None:
    """Add the minit install directory to PATH.

    \b
    Linux/macOS: appends export line to ~/.bashrc and ~/.zshrc (user),
                 and to /etc/environment (system, requires sudo).
    Windows:     runs setx to persist PATH for the current user,
                 and for the machine (system, requires admin shell).
    """
    from minit_cli._path_setup import add_to_path

    add_to_path(system=system)
