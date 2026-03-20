"""Configuration file management for minit-cli.

Config file: ~/.config/minit/config.toml

Sections
--------
[server]
  host           – bind host for the API server        (default: "127.0.0.1")
  port           – bind port for the API server        (default: 8000)
  interval       – collection interval in seconds      (default: 10)
  history_window – in-memory rolling window in seconds (default: 600)

[dashboard]
  refresh        – terminal refresh interval in seconds (default: 2.0)

[logging]
  log_path       – directory for metric log files      (default: ~/.local/share/minit/logs)
  retention_days – days to keep log files              (default: 7)

[thresholds]
  cpu_percent    – alert when CPU % >= this value; -1 = disabled (default: -1)
  memory_percent – alert when RAM % >= this value; -1 = disabled (default: -1)
  disk_percent   – alert when disk % >= this value; -1 = disabled (default: -1)
  hook           – shell command to run on alert; empty = disabled (default: "")
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    "server": {
        "host": "127.0.0.1",
        "port": 8000,
        "interval": 10,
        "history_window": 600,  # seconds of in-memory rolling window
    },
    "dashboard": {
        "refresh": 2.0,
    },
    "logging": {
        "log_path": str(Path.home() / ".local" / "share" / "minit" / "logs"),
        "retention_days": 7,
    },
    "thresholds": {
        # Values <= 0 are treated as disabled.
        "cpu_percent": -1,
        "memory_percent": -1,
        "disk_percent": -1,
        "hook": "",  # shell command to run on alert (empty = disabled)
    },
}

CONFIG_PATH = Path.home() / ".config" / "minit" / "config.toml"


def config_path() -> Path:
    """Return the path to the active config file."""
    return CONFIG_PATH


def load() -> dict[str, Any]:
    """Load config from file, merged on top of defaults."""
    cfg = copy.deepcopy(DEFAULTS)
    path = config_path()
    if not path.exists():
        return cfg
    try:
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]
        with open(path, "rb") as f:
            file_cfg = tomllib.load(f)
        _deep_merge(cfg, file_cfg)
    except Exception:
        pass  # Unreadable or malformed — fall back to defaults silently.
    return cfg


def save(cfg: dict[str, Any]) -> None:
    """Write config to the TOML file (creates parent dirs if needed)."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        _write_toml(f, cfg)


def get(key: str) -> Any:
    """Get a config value by dotted key (e.g. ``'server.host'``)."""
    cfg = load()
    parts = key.split(".")
    val: Any = cfg
    for part in parts:
        if not isinstance(val, dict) or part not in val:
            return None
        val = val[part]
    return val


def set_value(key: str, raw: str) -> None:
    """Set a dotted config key to a value (auto-coerced from string)."""
    cfg = load()
    parts = key.split(".")
    d: Any = cfg
    for part in parts[:-1]:
        d = d.setdefault(part, {})
    leaf = parts[-1]
    if raw.lower() in ("true", "false"):
        d[leaf] = raw.lower() == "true"
    else:
        try:
            d[leaf] = int(raw)
        except ValueError:
            try:
                d[leaf] = float(raw)
            except ValueError:
                d[leaf] = raw
    save(cfg)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def _write_toml(f: Any, cfg: dict[str, Any]) -> None:
    """Minimal TOML writer for flat-sectioned configs (no nested tables)."""
    # Top-level scalars first (uncommon, but supported)
    for k, v in cfg.items():
        if not isinstance(v, dict):
            f.write(f"{k} = {_toml_val(v)}\n")
    # One [section] per dict value
    for k, v in cfg.items():
        if isinstance(v, dict):
            f.write(f"\n[{k}]\n")
            for sk, sv in v.items():
                f.write(f"{sk} = {_toml_val(sv)}\n")


def _toml_val(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        return f'"{v.replace(chr(92), chr(92) + chr(92))}"'
    return str(v)
