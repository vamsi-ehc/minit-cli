"""CLI entry point for minit-cli.

Usage
-----
  minit dashboard            # real-time terminal dashboard
  minit serve                # start the JSON export API server
  minit stats                # print a one-shot JSON snapshot to stdout
  minit stats --pretty       # pretty-print the JSON snapshot
  minit stats --format table # tabular output
  minit stats --format csv   # CSV output
  minit stop                 # stop the running server
  minit status               # show server status
  minit config --show        # display current config values
  minit config --path        # print the config file path
  minit config set <k> <v>   # set a config key
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

_PID_FILE = os.path.expanduser("~/.minit_server.pid")


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
    from minit_cli import config as cfg_mod
    refresh = args.refresh if args.refresh is not None else cfg_mod.load()["dashboard"]["refresh"]
    run(refresh_interval=refresh)


def _cmd_serve(args: argparse.Namespace) -> None:
    import datetime
    import subprocess
    from minit_cli import config as cfg_mod

    cfg = cfg_mod.load()
    host = args.host if args.host is not None else cfg["server"]["host"]
    port = args.port if args.port is not None else cfg["server"]["port"]
    interval = args.interval if args.interval is not None else cfg["server"]["interval"]
    window = args.window if args.window is not None else cfg["server"]["history_window"]

    # Check if a server is already running.
    if os.path.exists(_PID_FILE):
        with open(_PID_FILE) as f:
            content = f.read().strip()
        try:
            parsed = json.loads(content)
            old_pid = parsed["pid"] if isinstance(parsed, dict) else int(parsed)
        except (json.JSONDecodeError, KeyError, ValueError):
            old_pid = int(content)
        try:
            os.kill(old_pid, 0)
            print(
                f"minit API server is already running (PID {old_pid}).\n"
                f"  Stop it with:  minit stop"
            )
            return
        except (OSError, ValueError):
            os.remove(_PID_FILE)

    # Launch the server as a detached background process.
    cmd = [
        sys.executable, "-m", "minit_cli._server_worker",
        "--host", host,
        "--port", str(port),
        "--interval", str(interval),
        "--window", str(window),
    ]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    pid_data = {
        "pid": proc.pid,
        "host": host,
        "port": port,
        "started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    with open(_PID_FILE, "w") as f:
        json.dump(pid_data, f)

    base_url = f"http://{host}:{port}"
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
        f"  Stop the server:\n"
        f"    minit stop"
    )


def _cmd_stop(_args: argparse.Namespace) -> None:
    import signal

    if not os.path.exists(_PID_FILE):
        print("No running minit server found.")
        return

    with open(_PID_FILE) as f:
        content = f.read().strip()
    try:
        pid = json.loads(content)["pid"]
    except (json.JSONDecodeError, KeyError):
        pid = int(content)

    try:
        if platform.system() == "Windows":
            import subprocess
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                check=True,
                capture_output=True,
            )
        else:
            os.kill(pid, signal.SIGTERM)
        os.remove(_PID_FILE)
        print(f"Stopped minit server (PID {pid}).")
    except (OSError, Exception):
        os.remove(_PID_FILE)
        print(f"Server (PID {pid}) was not running. Cleaned up PID file.")


def _cmd_status(_args: argparse.Namespace) -> None:
    import datetime

    if not os.path.exists(_PID_FILE):
        print("minit server: stopped")
        return

    with open(_PID_FILE) as f:
        content = f.read().strip()

    try:
        data = json.loads(content)
        if isinstance(data, dict):
            pid = data["pid"]
            host = data.get("host", "127.0.0.1")
            port = data.get("port", 8000)
            started = data.get("started")
        else:
            pid = int(data)
            host, port, started = "127.0.0.1", 8000, None
    except (json.JSONDecodeError, KeyError, ValueError):
        pid = int(content)
        host, port, started = "127.0.0.1", 8000, None

    try:
        os.kill(pid, 0)
        running = True
    except OSError:
        running = False

    if not running:
        print(f"minit server: stopped  (stale PID file for {pid})")
        return

    print("minit server: running")
    print(f"  PID:     {pid}")
    print(f"  host:    {host}")
    print(f"  port:    {port}")
    if started:
        start_dt = datetime.datetime.fromisoformat(started)
        uptime = datetime.datetime.now(datetime.timezone.utc) - start_dt
        total_s = int(uptime.total_seconds())
        h, m, s = total_s // 3600, (total_s % 3600) // 60, total_s % 60
        print(f"  uptime:  {h:02d}:{m:02d}:{s:02d}")


def _cmd_logs(args: argparse.Namespace) -> None:
    from minit_cli import config as cfg_mod, metrics_log

    log_dir: str = cfg_mod.load()["logging"]["log_path"]

    since = None
    until = None
    if args.since:
        try:
            since = metrics_log.parse_since(args.since)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    if args.until:
        try:
            until = metrics_log.parse_since(args.until)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    date = None
    if args.date:
        import datetime
        try:
            date = datetime.date.fromisoformat(args.date)
        except ValueError:
            print(f"Error: invalid date {args.date!r} (expected YYYY-MM-DD)", file=sys.stderr)
            sys.exit(1)

    indent = 2 if args.pretty else None

    if args.follow:
        print(f"Tailing {log_dir} ... (Ctrl+C to stop)", file=sys.stderr)
        try:
            for entry in metrics_log.follow_log(log_dir):
                print(json.dumps(entry, indent=indent))
        except KeyboardInterrupt:
            pass
        return

    count = 0
    for entry in metrics_log.iter_entries(log_dir, since=since, until=until, date=date):
        print(json.dumps(entry, indent=indent))
        count += 1

    if count == 0:
        print("No log entries found.", file=sys.stderr)


def _cmd_config(args: argparse.Namespace) -> None:
    from minit_cli import config as cfg_mod

    if getattr(args, "config_action", None) == "set":
        cfg_mod.set_value(args.key, args.value)
        print(f"Set {args.key} = {args.value}")
        return

    if args.path:
        print(cfg_mod.config_path())
        return

    # Default: --show or bare `minit config`
    cfg = cfg_mod.load()
    for section, values in cfg.items():
        if isinstance(values, dict):
            print(f"[{section}]")
            for k, v in values.items():
                print(f"  {k} = {v}")
        else:
            print(f"{section} = {values}")


def _cmd_stats(args: argparse.Namespace) -> None:
    import csv
    import datetime
    import io
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

    fmt = args.format

    if fmt == "json":
        indent = 2 if args.pretty else None
        print(json.dumps(snapshot, indent=indent))
        return

    # Build a flat list of (key, value) rows for table / csv output.
    rows = [
        ("timestamp", snapshot["timestamp"]),
        ("cpu.overall_percent", snapshot["cpu"]["overall_percent"]),
        ("cpu.count_logical", snapshot["cpu"]["count_logical"]),
        ("cpu.count_physical", snapshot["cpu"]["count_physical"]),
        ("cpu.freq_mhz", snapshot["cpu"]["freq_mhz"]),
        ("memory.virtual.total_mb", snapshot["memory"]["virtual"]["total_mb"]),
        ("memory.virtual.used_mb", snapshot["memory"]["virtual"]["used_mb"]),
        ("memory.virtual.available_mb", snapshot["memory"]["virtual"]["available_mb"]),
        ("memory.virtual.percent", snapshot["memory"]["virtual"]["percent"]),
        ("memory.swap.total_mb", snapshot["memory"]["swap"]["total_mb"]),
        ("memory.swap.used_mb", snapshot["memory"]["swap"]["used_mb"]),
        ("memory.swap.percent", snapshot["memory"]["swap"]["percent"]),
    ]
    for i, part in enumerate(snapshot["disk"]["partitions"]):
        prefix = f"disk.partitions[{i}]"
        rows.append((f"{prefix}.device", part["device"]))
        rows.append((f"{prefix}.mountpoint", part["mountpoint"]))
        rows.append((f"{prefix}.total_gb", part["total_gb"]))
        rows.append((f"{prefix}.used_gb", part["used_gb"]))
        rows.append((f"{prefix}.percent", part["percent"]))

    if fmt == "table":
        key_width = max(len(r[0]) for r in rows)
        print(f"{'KEY':<{key_width}}  VALUE")
        print("-" * (key_width + 2 + 20))
        for key, val in rows:
            print(f"{key:<{key_width}}  {val}")
        return

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["key", "value"])
        writer.writerows(rows)
        print(buf.getvalue(), end="")
        return


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
        "--refresh", default=1.2, type=float, metavar="SECONDS",
        help="Dashboard refresh interval in seconds. (default: 1.2)",
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
            "  GET /health        – liveness probe\n\n"
            "CLI flags override the config file values."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_serve.add_argument("--host", default=None, help="Bind host. (default: from config, 127.0.0.1)")
    p_serve.add_argument("--port", default=None, type=int, help="Bind port. (default: from config, 8000)")
    p_serve.add_argument(
        "--interval", default=None, type=int, metavar="SECONDS",
        help="Stats collection interval in seconds. (default: from config, 10)",
    )
    p_serve.add_argument(
        "--window", default=None, type=int, metavar="SECONDS",
        help="In-memory rolling window duration in seconds. (default: from config, 600)",
    )

    # stop
    subparsers.add_parser("stop", help="Stop the running minit API server.")

    # status
    subparsers.add_parser(
        "status", help="Show whether the minit API server is running."
    )

    # stats
    p_stats = subparsers.add_parser(
        "stats", help="Print a one-shot snapshot of all machine statistics to stdout."
    )
    p_stats.add_argument(
        "--pretty", action="store_true", default=False, help="Pretty-print JSON output."
    )
    p_stats.add_argument(
        "--format", default="json", choices=["json", "table", "csv"],
        metavar="FORMAT",
        help="Output format: json (default), table, or csv.",
    )

    # logs
    p_logs = subparsers.add_parser(
        "logs",
        help="View stored metric log files.",
        description=(
            "View stored metric log files (~/.local/share/minit/logs/).\n\n"
            "  minit logs                    – print all entries from today\n"
            "  minit logs --date 2024-01-15  – entries for a specific date\n"
            "  minit logs --since 1h         – entries from the last hour\n"
            "  minit logs --since 30m        – entries from the last 30 minutes\n"
            "  minit logs --follow           – tail live entries (Ctrl+C to stop)\n"
            "  minit logs --pretty           – pretty-print JSON"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_logs.add_argument("--follow", "-f", action="store_true", help="Tail the log in real time.")
    p_logs.add_argument("--since", metavar="TIME", help="Show entries after TIME (e.g. 1h, 30m, 2024-01-15T10:00:00).")
    p_logs.add_argument("--until", metavar="TIME", help="Show entries before TIME.")
    p_logs.add_argument("--date", metavar="DATE", help="Show entries for a specific date (YYYY-MM-DD).")
    p_logs.add_argument("--pretty", action="store_true", default=False, help="Pretty-print JSON output.")

    # config
    p_config = subparsers.add_parser(
        "config",
        help="Manage minit configuration.",
        description=(
            "Manage minit configuration (~/.config/minit/config.toml).\n\n"
            "  minit config           – show current values\n"
            "  minit config --path    – print the config file path\n"
            "  minit config --show    – show current values\n"
            "  minit config set <key> <value>  – set a value (e.g. server.port 9000)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_config.add_argument(
        "--path", action="store_true", help="Print the active config file path."
    )
    p_config.add_argument(
        "--show", action="store_true", help="Show current config values (default)."
    )
    config_sub = p_config.add_subparsers(dest="config_action")
    p_config_set = config_sub.add_parser("set", help="Set a config key to a value.")
    p_config_set.add_argument("key", help="Dotted key, e.g. server.host")
    p_config_set.add_argument("value", help="New value")

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
    elif args.command == "stop":
        _cmd_stop(args)
    elif args.command == "status":
        _cmd_status(args)
    elif args.command == "stats":
        _cmd_stats(args)
    elif args.command == "logs":
        _cmd_logs(args)
    elif args.command == "config":
        _cmd_config(args)
    elif args.command == "setup":
        _cmd_setup(args)
    else:
        parser.print_help()
