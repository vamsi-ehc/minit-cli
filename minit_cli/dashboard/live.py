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
└─────────────────────────────────────────────┘
"""

from __future__ import annotations

import datetime
import platform
import socket
import time

import psutil
from rich import box
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from minit_cli.collectors import cpu, memory, disk, network, processes


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _color_pct(pct: float) -> str:
    if pct >= 90:
        return "bold red"
    if pct >= 70:
        return "yellow"
    return "green"


def _make_cpu_panel() -> Panel:
    data = cpu.collect()
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("Core", style="cyan", no_wrap=True)
    table.add_column("Usage", no_wrap=True)
    table.add_column("%", justify="right")

    for i, pct in enumerate(data["per_core_percent"]):
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        table.add_row(
            f"CPU{i}",
            f"[{_color_pct(pct)}]{bar}[/]",
            f"[{_color_pct(pct)}]{pct:5.1f}%[/]",
        )

    freq = f"  {data['freq_mhz']} MHz" if data["freq_mhz"] else ""
    subtitle = (
        f"Overall: [bold]{data['overall_percent']:.1f}%[/]  "
        f"Logical: {data['count_logical']}  "
        f"Physical: {data['count_physical']}{freq}"
    )
    return Panel(table, title="[bold cyan]CPU[/]", subtitle=subtitle, border_style="cyan")


def _make_memory_panel() -> Panel:
    data = memory.collect()
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
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        table.add_row(
            label,
            f"[{_color_pct(pct)}]{bar}[/]",
            f"[{_color_pct(pct)}]{pct:.1f}%[/] {used:.0f}/{total:.0f} MB",
        )

    return Panel(table, title="[bold magenta]Memory[/]", border_style="magenta")


def _make_disk_panel() -> Panel:
    data = disk.collect()
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("Mount", style="cyan", no_wrap=True)
    table.add_column("FS", style="dim")
    table.add_column("Bar")
    table.add_column("Used/Total", justify="right")
    table.add_column("I/O R/W MB", justify="right")

    io = data["io"]

    for part in data["partitions"]:
        pct = part["percent"]
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))

        # Try to match the disk I/O entry by device base name
        dev_base = part["device"].rstrip("/").split("/")[-1].split("\\")[-1]
        io_str = "n/a"
        for key in io:
            if dev_base and (dev_base in key or key in dev_base):
                io_str = f"{io[key]['read_mb']:.1f} / {io[key]['write_mb']:.1f}"
                break

        table.add_row(
            part["mountpoint"],
            part["fstype"],
            f"[{_color_pct(pct)}]{bar}[/]",
            f"[{_color_pct(pct)}]{pct:.1f}%[/]  {part['used_gb']:.1f}/{part['total_gb']:.1f} GB",
            io_str,
        )

    return Panel(table, title="[bold yellow]Disk[/]", border_style="yellow")


def _make_network_panel() -> Panel:
    data = network.collect()
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


def _make_process_panel(limit: int = 15) -> Panel:
    data = processes.collect(limit=limit)
    table = Table(box=box.SIMPLE, show_header=True, expand=True)
    table.add_column("PID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name")
    table.add_column("User", style="dim")
    table.add_column("Status", style="dim")
    table.add_column("CPU%", justify="right")
    table.add_column("Mem%", justify="right")

    for proc in data["processes"]:
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


def _make_header() -> Text:
    hostname = socket.gethostname()
    os_info = f"{platform.system()} {platform.release()}"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = Text()
    text.append("  minit-cli  ", style="bold white on dark_blue")
    text.append(f"  {hostname}  ", style="bold")
    text.append(f"  {os_info}  ", style="dim")
    text.append(f"  {now}  ", style="italic")
    text.append("  [Visit: minit-cli.vamsi-tech.org]  ", style="dim cyan")
    return text


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(refresh_interval: float = 2.0) -> None:
    """Start the live dashboard.  Press Ctrl+C to quit."""
    # Prime psutil's CPU percent (first call always returns 0.0)
    psutil.cpu_percent(interval=None, percpu=True)
    time.sleep(0.1)

    console = Console()

    def _build() -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=1),
            Layout(name="top", size=None),
            Layout(name="disk", size=None),
            Layout(name="procs", size=None),
        )
        layout["top"].split_row(
            Layout(_make_cpu_panel(), name="cpu"),
            Layout(_make_memory_panel(), name="mem"),
            Layout(_make_network_panel(), name="net"),
        )
        layout["header"].update(_make_header())
        layout["disk"].update(_make_disk_panel())
        layout["procs"].update(_make_process_panel())
        return layout

    with Live(_build(), console=console, refresh_per_second=1, screen=True) as live:
        try:
            while True:
                time.sleep(refresh_interval)
                live.update(_build())
        except KeyboardInterrupt:
            pass
