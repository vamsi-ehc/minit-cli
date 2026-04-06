"""Real-time terminal dashboard using *rich*.

Layout (refreshed every ``refresh_interval`` seconds):
┌─────────────────────────────────────────────┐
│  Header: hostname + timestamp               │
├────────────┬────────────┬───────────────────┤
│  CPU cores │  Memory    │  Network          │
├────────────┴────────────┴───────────────────┤
│  Disk partitions                            │
├─────────────────────────────────────────────┤
│  Top processes                              │
├─────────────────────────────────────────────┤
│  Logged-in users                            │
└─────────────────────────────────────────────┘
"""

from __future__ import annotations

import datetime
import platform
import socket
import time
from concurrent.futures import ThreadPoolExecutor

import psutil
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from minit_cli.collectors import cpu, memory, disk, network, processes
from minit_cli.collectors import users as users_collector


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _color_pct(pct: float) -> str:
    if pct >= 90:
        return "bold red"
    if pct >= 70:
        return "yellow"
    return "green"


def _bar(pct: float, width: int = 20) -> str:
    filled = int(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


# ---------------------------------------------------------------------------
# Panel builders — accept pre-collected data (no psutil calls here)
# ---------------------------------------------------------------------------

def _make_cpu_panel(data: dict) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("Core", style="cyan", no_wrap=True)
    table.add_column("Usage", no_wrap=True)
    table.add_column("%", justify="right")

    for i, pct in enumerate(data["per_core_percent"]):
        col = _color_pct(pct)
        table.add_row(
            f"CPU{i}",
            f"[{col}]{_bar(pct)}[/]",
            f"[{col}]{pct:5.1f}%[/]",
        )

    freq = f"  {data['freq_mhz']} MHz" if data["freq_mhz"] else ""
    subtitle = (
        f"Overall: [bold]{data['overall_percent']:.1f}%[/]  "
        f"Logical: {data['count_logical']}  "
        f"Physical: {data['count_physical']}{freq}"
    )
    return Panel(table, title="[bold cyan]CPU[/]", subtitle=subtitle, border_style="cyan")


def _make_memory_panel(data: dict) -> Panel:
    vm = data["virtual"]
    sw = data["swap"]

    table = Table(box=box.SIMPLE, show_header=False, expand=True)
    table.add_column("Label", style="cyan")
    table.add_column("Bar")
    table.add_column("Info", justify="right")

    for label, pct, used, total in [
        ("RAM ", vm["percent"], vm["used_mb"], vm["total_mb"]),
        ("Swap", sw["percent"], sw["used_mb"], sw["total_mb"]),
    ]:
        col = _color_pct(pct)
        table.add_row(
            label,
            f"[{col}]{_bar(pct)}[/]",
            f"[{col}]{pct:.1f}%[/] {used:.0f}/{total:.0f} MB",
        )

    return Panel(table, title="[bold magenta]Memory[/]", border_style="magenta")


def _make_disk_panel(data: dict) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("Mount", style="cyan", no_wrap=True)
    table.add_column("FS", style="dim")
    table.add_column("Bar")
    table.add_column("Used/Total", justify="right")
    table.add_column("I/O R/W MB", justify="right")

    io = data["io"]
    for part in data["partitions"]:
        pct = part["percent"]
        dev_base = part["device"].rstrip("/").split("/")[-1].split("\\")[-1]
        io_str = "n/a"
        for key in io:
            if dev_base and (dev_base in key or key in dev_base):
                io_str = f"{io[key]['read_mb']:.1f} / {io[key]['write_mb']:.1f}"
                break
        col = _color_pct(pct)
        table.add_row(
            part["mountpoint"],
            part["fstype"],
            f"[{col}]{_bar(pct)}[/]",
            f"[{col}]{pct:.1f}%[/]  {part['used_gb']:.1f}/{part['total_gb']:.1f} GB",
            io_str,
        )

    return Panel(table, title="[bold yellow]Disk[/]", border_style="yellow")


def _make_network_panel(data: dict) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("NIC", style="cyan", no_wrap=True)
    table.add_column("Sent MB", justify="right")
    table.add_column("Recv MB", justify="right")
    table.add_column("Pkts Sent", justify="right")
    table.add_column("Pkts Recv", justify="right")
    table.add_column("Err/Drop", justify="right")

    for nic, stats in data["interfaces"].items():
        table.add_row(
            nic,
            f"{stats['bytes_sent_mb']:.1f}",
            f"{stats['bytes_recv_mb']:.1f}",
            str(stats["packets_sent"]),
            str(stats["packets_recv"]),
            f"{stats['errin'] + stats['errout']}/{stats['dropin'] + stats['dropout']}",
        )

    return Panel(table, title="[bold blue]Network[/]", border_style="blue")


def _make_users_panel(data: dict) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("User", style="cyan", no_wrap=True)
    table.add_column("Terminal", style="dim")
    table.add_column("Host", style="dim")
    table.add_column("Since", justify="right", style="dim")

    for u in data["users"]:
        table.add_row(u["name"], u["terminal"], u["host"], u["started"])

    if not data["users"]:
        table.add_row("[dim]no users logged in[/]", "", "", "")

    count = len(data["users"])
    return Panel(
        table,
        title=f"[bold white]Logged-in Users ({count})[/]",
        border_style="white",
    )


def _make_process_panel(data: dict) -> Panel:
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("PID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("User", style="dim")
    table.add_column("Status", style="dim")
    table.add_column("CPU%", justify="right")
    table.add_column("Mem%", justify="right")

    for proc in data["processes"][:15]:
        cpu_pct = proc["cpu_percent"]
        table.add_row(
            str(proc["pid"]),
            proc["name"],
            proc["username"],
            proc["status"],
            f"[{_color_pct(cpu_pct)}]{cpu_pct:.1f}[/]",
            f"{proc['memory_percent']:.2f}",
        )

    return Panel(table, title="[bold green]Processes (top by CPU)[/]", border_style="green")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

_COLLECTORS = (
    cpu.collect,
    memory.collect,
    disk.collect,
    network.collect,
    processes.collect,
    users_collector.collect,
)


def run(refresh_interval: float = 1.2) -> None:
    """Start the live dashboard.  Press Ctrl+C to quit."""
    # Cache values that never change during a session — avoids repeated syscalls
    hostname = socket.gethostname()
    os_info  = f"{platform.system()} {platform.release()}"

    # Prime psutil's CPU percent (first call always returns 0.0)
    psutil.cpu_percent(interval=None, percpu=True)
    time.sleep(0.1)

    console = Console()

    # Build the layout skeleton once and reuse it — avoids reallocating the
    # entire object tree every refresh tick.
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=1),
        Layout(name="top"),
        Layout(name="disk"),
        Layout(name="procs"),
        Layout(name="users", size=8),
    )
    layout["top"].split_row(
        Layout(name="cpu"),
        Layout(name="mem"),
        Layout(name="net"),
    )

    # Persistent pool — threads stay alive between refreshes, avoiding the
    # overhead of spawning new threads each cycle.
    executor = ThreadPoolExecutor(max_workers=6, thread_name_prefix="minit-col")

    def _refresh() -> None:
        """Collect all metrics in parallel, then update layout panels."""
        futures = [executor.submit(fn) for fn in _COLLECTORS]
        cpu_d, mem_d, disk_d, net_d, proc_d, users_d = (f.result() for f in futures)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hdr = Text()
        hdr.append("  minit-cli  ", style="bold white on dark_blue")
        hdr.append(f"  {hostname}  ", style="bold")
        hdr.append(f"  {os_info}  ", style="dim")
        hdr.append(f"  {now}  ", style="italic")

        layout["header"].update(hdr)
        layout["cpu"].update(_make_cpu_panel(cpu_d))
        layout["mem"].update(_make_memory_panel(mem_d))
        layout["net"].update(_make_network_panel(net_d))
        layout["disk"].update(_make_disk_panel(disk_d))
        layout["procs"].update(_make_process_panel(proc_d))
        layout["users"].update(_make_users_panel(users_d))

    _refresh()

    # Match Rich's internal render rate to the data refresh rate so it doesn't
    # spin and waste CPU re-drawing the same content.
    rps = max(1, round(1.0 / refresh_interval))
    with Live(layout, console=console, refresh_per_second=rps, screen=True):
        try:
            while True:
                time.sleep(refresh_interval)
                _refresh()
        except KeyboardInterrupt:
            pass
        finally:
            executor.shutdown(wait=False)
