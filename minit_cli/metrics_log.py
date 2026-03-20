"""Metrics log file management for minit-cli.

Daily snapshot logs are stored as JSON Lines at:
  <log_path>/YYYY-MM-DD.jsonl

Alert events are appended to:
  <log_path>/alerts.jsonl
"""

from __future__ import annotations

import datetime
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterator, Optional


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def write_snapshot(snapshot: Dict[str, Any], log_dir: str) -> None:
    """Append a snapshot to today's JSON Lines log file."""
    path = Path(log_dir) / f"{datetime.date.today().isoformat()}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot) + "\n")


def write_alert(event: Dict[str, Any], log_dir: str) -> None:
    """Append an alert event to alerts.jsonl."""
    path = Path(log_dir) / "alerts.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------

def rotate_logs(log_dir: str, retention_days: int) -> None:
    """Delete daily log files older than *retention_days* days."""
    cutoff = datetime.date.today() - datetime.timedelta(days=retention_days)
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    for f in log_path.glob("????-??-??.jsonl"):
        try:
            if datetime.date.fromisoformat(f.stem) < cutoff:
                f.unlink()
        except (ValueError, OSError):
            pass


# ---------------------------------------------------------------------------
# Threshold checking
# ---------------------------------------------------------------------------

def check_thresholds(
    snapshot: Dict[str, Any],
    thresholds: Dict[str, Any],
    log_dir: str,
) -> None:
    """Compare snapshot values against configured thresholds and log alerts."""
    ts = snapshot.get("timestamp", datetime.datetime.now(datetime.timezone.utc).isoformat())

    def _alert(metric: str, value: float, threshold: float, **extra: Any) -> None:
        event = {"timestamp": ts, "metric": metric, "value": value, "threshold": threshold}
        event.update(extra)
        write_alert(event, log_dir)
        _run_hook(thresholds.get("hook", ""), event)

    cpu_thresh = _thresh(thresholds.get("cpu_percent"))
    if cpu_thresh is not None:
        cpu_val = snapshot.get("cpu", {}).get("overall_percent", 0)
        if cpu_val >= cpu_thresh:
            _alert("cpu_percent", cpu_val, cpu_thresh)

    mem_thresh = _thresh(thresholds.get("memory_percent"))
    if mem_thresh is not None:
        mem_val = snapshot.get("memory", {}).get("virtual", {}).get("percent", 0)
        if mem_val >= mem_thresh:
            _alert("memory_percent", mem_val, mem_thresh)

    disk_thresh = _thresh(thresholds.get("disk_percent"))
    if disk_thresh is not None:
        for part in snapshot.get("disk", {}).get("partitions", []):
            if part.get("percent", 0) >= disk_thresh:
                _alert("disk_percent", part["percent"], disk_thresh, mountpoint=part["mountpoint"])


def _thresh(val: Any) -> Optional[float]:
    """Return the threshold as a float, or None if disabled (<= 0 or missing)."""
    if val is None:
        return None
    try:
        f = float(val)
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None


def _run_hook(hook: str, event: Dict[str, Any]) -> None:
    """Run the user-configured shell hook with alert info in env vars."""
    if not hook or not hook.strip():
        return
    import os
    import subprocess
    env = os.environ.copy()
    env["MINIT_ALERT_METRIC"] = event.get("metric", "")
    env["MINIT_ALERT_VALUE"] = str(event.get("value", ""))
    env["MINIT_ALERT_THRESHOLD"] = str(event.get("threshold", ""))
    env["MINIT_ALERT_TIMESTAMP"] = event.get("timestamp", "")
    env["MINIT_ALERT_MOUNTPOINT"] = event.get("mountpoint", "")
    try:
        subprocess.Popen(hook, shell=True, env=env)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Reading / iteration
# ---------------------------------------------------------------------------

def parse_since(value: str) -> datetime.datetime:
    """Parse a --since / --until value into an aware UTC datetime.

    Accepts:
      ``Xh``  – X hours ago
      ``Xm``  – X minutes ago
      ``Xs``  – X seconds ago
      ISO 8601 datetime string
      YYYY-MM-DD date (interpreted as start of that day UTC)
    """
    value = value.strip()
    now = datetime.datetime.now(datetime.timezone.utc)
    if value.endswith("h") and value[:-1].isdigit():
        return now - datetime.timedelta(hours=int(value[:-1]))
    if value.endswith("m") and value[:-1].isdigit():
        return now - datetime.timedelta(minutes=int(value[:-1]))
    if value.endswith("s") and value[:-1].isdigit():
        return now - datetime.timedelta(seconds=int(value[:-1]))
    # Try ISO datetime first, then date-only
    try:
        dt = datetime.datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except ValueError:
        pass
    try:
        d = datetime.date.fromisoformat(value)
        return datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc)
    except ValueError:
        raise ValueError(f"Cannot parse time value: {value!r}")


def iter_entries(
    log_dir: str,
    since: Optional[datetime.datetime] = None,
    until: Optional[datetime.datetime] = None,
    date: Optional[datetime.date] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield log entries from daily JSONL files, with optional filtering."""
    log_path = Path(log_dir)
    if not log_path.exists():
        return
    if date is not None:
        files = sorted(log_path.glob(f"{date.isoformat()}.jsonl"))
    else:
        files = sorted(log_path.glob("????-??-??.jsonl"))
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if since is not None or until is not None:
                        ts_str = entry.get("timestamp", "")
                        try:
                            ts = datetime.datetime.fromisoformat(ts_str)
                            if ts.tzinfo is None:
                                ts = ts.replace(tzinfo=datetime.timezone.utc)
                            if since is not None and ts < since:
                                continue
                            if until is not None and ts > until:
                                continue
                        except ValueError:
                            pass
                    yield entry
        except OSError:
            pass


def follow_log(log_dir: str) -> Iterator[Dict[str, Any]]:
    """Tail today's log file, yielding new entries as they are written.

    Blocks indefinitely; the caller should handle KeyboardInterrupt.
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    def _today_file() -> Path:
        return log_path / f"{datetime.date.today().isoformat()}.jsonl"

    current_path = _today_file()
    current_path.touch()

    with open(current_path, encoding="utf-8") as fh:
        fh.seek(0, 2)  # jump to end
        while True:
            # If the day rolled over, reopen the new file.
            new_path = _today_file()
            if new_path != current_path:
                current_path = new_path
                current_path.touch()
                fh.close()
                fh = open(current_path, encoding="utf-8")

            line = fh.readline()
            if line:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        pass
            else:
                time.sleep(0.5)
