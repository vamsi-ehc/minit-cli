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

import argparse
import json
import os
import platform
import sys
from pathlib import Path

from minit_cli import __version__


def _maybe_prompt_path_setup() -> None:
    """Offer once to add the minit bin directory to PATH if it is missing.

    Skips silently when:
      - The bin dir is already in PATH.
      - A sentinel file records that the user already answered.
      - stdout/stdin are not a TTY (non-interactive context).
    """
    bin_dir = str(Path(sys.executable).parent)
    sep = ";" if platform.system() == "Windows" else ":"
    if bin_dir in os.environ.get("PATH", "").split(sep):
        return  # Already on PATH – nothing to do.

    sentinel = Path.home() / ".config" / "minit" / ".path_setup_done"
    if sentinel.exists():
        return  # User already answered; don't pester again.

    if not sys.stdout.isatty() or not sys.stdin.isatty():
        return  # Non-interactive – skip the prompt.

    print(
        f"\n[minit] The install directory '{bin_dir}' is not in your PATH.\n"
        f"        You won't be able to run 'minit' until it is added.",
        file=sys.stderr,
    )

    # Persist the answer regardless of what the user picks so we only ask once.
    sentinel.parent.mkdir(parents=True, exist_ok=True)
    sentinel.touch()

    try:
        answer = input("  Add it to your PATH now? [Y/n] ").strip().lower()
        if answer in ("", "y", "yes"):
            from minit_cli._path_setup import add_to_path
            add_to_path(system=False)
        else:
            print(
                "  Skipped. Run 'minit setup' any time to add it later.",
                file=sys.stderr,
            )
    except (KeyboardInterrupt, EOFError):
        pass


def _cmd_dashboard(args: argparse.Namespace) -> None:
    from minit_cli.dashboard.live import run
    run(refresh_interval=args.refresh)


def _cmd_serve(args: argparse.Namespace) -> None:
    import subprocess

    pid_file = os.path.expanduser("~/.minit_server.pid")

    # Check if a server is already running.
    if os.path.exists(pid_file):
        with open(pid_file) as f:
            old_pid = f.read().strip()
        try:
            os.kill(int(old_pid), 0)
            print(
                f"minit API server is already running (PID {old_pid}).\n"
                f"  Stop it with:  kill {old_pid}"
            )
            return
        except (OSError, ValueError):
            os.remove(pid_file)

    # Launch the server as a detached background process.
    cmd = [
        sys.executable, "-m", "minit_cli._server_worker",
        "--host", args.host,
        "--port", str(args.port),
        "--interval", str(args.interval),
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    with open(pid_file, "w") as f:
        f.write(str(proc.pid))

    base_url = f"http://{args.host}:{args.port}"
    print(
        f"minit API server started in the background (PID {proc.pid}).\n"
        f"\n"
        f"  Web dashboard:\n"
        f"    {base_url}/\n"
        f"\n"
        f"  API endpoints:\n"
        f"    {base_url}/stats         – last 10 min of snapshots\n"
        f"    {base_url}/stats/latest  – most recent snapshot\n"
        f"    {base_url}/sysinfo       – system information\n"
        f"    {base_url}/health        – liveness probe\n"
        f"\n"
        f"  Customize host / port / interval:\n"
        f"    minit serve --port 9000\n"
        f"    minit serve --host 0.0.0.0 --port 9000\n"
        f"    minit serve --host 0.0.0.0 --port 9000 --interval 5\n"
        f"\n"
        f"  Stop the server:\n"
        f"    kill {proc.pid}"
    )


def _cmd_stats(args: argparse.Namespace) -> None:
    import datetime
    import time

    import psutil

    from minit_cli.collectors import cpu, memory, disk, network, processes

    # Prime psutil (first call always returns 0.0)
    psutil.cpu_percent(interval=None, percpu=True)
    time.sleep(0.2)

    snapshot = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cpu": cpu.collect(),
        "memory": memory.collect(),
        "disk": disk.collect(),
        "network": network.collect(),
        "processes": processes.collect(),
    }
    indent = 2 if args.pretty else None
    print(json.dumps(snapshot, indent=indent))


def _cmd_setup(args: argparse.Namespace) -> None:
    from minit_cli._path_setup import add_to_path
    add_to_path(system=args.system)


def main() -> None:
    """minit-cli – real-time machine stats dashboard and export API."""
    parser = argparse.ArgumentParser(
        prog="minit",
        description="minit-cli – real-time machine stats dashboard and export API.",
    )
    parser.add_argument(
        "--version", action="version", version=f"minit {__version__}"
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # dashboard
    p_dashboard = subparsers.add_parser(
        "dashboard", help="Launch the real-time terminal dashboard. Press Ctrl+C to quit."
    )
    p_dashboard.add_argument(
        "--refresh", default=2.0, type=float, metavar="SECONDS",
        help="Dashboard refresh interval in seconds. (default: 2.0)",
    )

    # serve
    p_serve = subparsers.add_parser(
        "serve",
        help="Start the JSON export API server in the background.",
        description=(
            "Start the JSON export API server in the background.\n\n"
            "Collects stats every INTERVAL seconds and exposes them at:\n"
            "  GET /stats         – last 10 minutes of snapshots\n"
            "  GET /stats/latest  – most recent snapshot\n"
            "  GET /health        – liveness probe"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_serve.add_argument("--host", default="127.0.0.1", help="Bind host. (default: 127.0.0.1)")
    p_serve.add_argument("--port", default=8000, type=int, help="Bind port. (default: 8000)")
    p_serve.add_argument(
        "--interval", default=10, type=int, metavar="SECONDS",
        help="Stats collection interval in seconds. (default: 10)",
    )

    # stats
    p_stats = subparsers.add_parser(
        "stats", help="Print a one-shot JSON snapshot of all machine statistics to stdout."
    )
    p_stats.add_argument(
        "--pretty", action="store_true", default=False, help="Pretty-print JSON output."
    )

    # setup
    p_setup = subparsers.add_parser(
        "setup",
        help="Add the minit install directory to PATH.",
        description=(
            "Add the minit install directory to PATH.\n\n"
            "Linux/macOS: appends export line to ~/.bashrc and ~/.zshrc (user),\n"
            "             and to /etc/environment (system, requires sudo).\n"
            "Windows:     runs setx to persist PATH for the current user,\n"
            "             and for the machine (system, requires admin shell)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_setup.add_argument(
        "--system", action="store_true", default=False,
        help="Also add to system-wide PATH (requires admin/root privileges).",
    )

    _maybe_prompt_path_setup()

    args = parser.parse_args()

    if args.command == "dashboard":
        _cmd_dashboard(args)
    elif args.command == "serve":
        _cmd_serve(args)
    elif args.command == "stats":
        _cmd_stats(args)
    elif args.command == "setup":
        _cmd_setup(args)
    else:
        parser.print_help()
