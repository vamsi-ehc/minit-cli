# minit-cli — Usage Guide

minit-cli is a real-time machine-stats CLI with a terminal dashboard and a JSON export API.

---

## Installation

### From PyPI (recommended)

```bash
pip install minit-cli
minit setup          # add minit to PATH
```

> If `minit` is not found after install, run `python -m minit_cli.cli setup` and restart your shell.

### From source

```bash
git clone https://github.com/vamsi-ehc/minit-cli
cd minit-cli
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### Standalone binary (PyInstaller build)

```bash
pip install pyinstaller
pyinstaller minit.spec
# Produces:
#   dist/minit                  (Linux / macOS)
#   dist\minit.exe              (Windows)
#   dist/minit-server-worker    (required for `minit serve`)
```

Copy both `minit` and `minit-server-worker` to the same directory and add it to PATH.

---

## Quick start

```bash
minit dashboard          # open the live terminal dashboard
minit stats --pretty     # print a one-shot JSON snapshot
minit serve              # start the background HTTP API server
```

---

## Commands

### `minit dashboard`

Launch the full-screen terminal dashboard. Press **Ctrl-C** to quit.

```
minit dashboard              # refresh every 2 seconds (default)
minit dashboard --refresh 5  # refresh every 5 seconds
```

The dashboard displays:

| Section | What is shown |
|---|---|
| CPU | Per-core bars, overall %, frequency |
| Memory | RAM and swap usage (MB / %) |
| Disk space | Per-partition used / free / total |
| Disk I/O | Cumulative read and write bytes per disk |
| Network | Per-NIC bytes, packets, errors, drops |
| Processes | Top-10 processes sorted by CPU % |

**Options**

| Flag | Default | Description |
|---|---|---|
| `--refresh SECONDS` | `2.0` | Redraw interval in seconds |

---

### `minit serve`

Start the JSON API server as a background process. Stats are collected every `--interval` seconds and the last 10 minutes of snapshots are kept in memory.

```bash
minit serve                                      # http://127.0.0.1:8000
minit serve --port 9000                          # custom port
minit serve --host 0.0.0.0 --port 9000          # listen on all interfaces
minit serve --host 0.0.0.0 --port 9000 --interval 5
```

**Options**

| Flag | Default | Description |
|---|---|---|
| `--host HOST` | `127.0.0.1` | Bind address |
| `--port PORT` | `8000` | Bind port |
| `--interval SECONDS` | `10` | Stats collection interval |

**API endpoints**

| Method | Path | Response |
|---|---|---|
| `GET` | `/` | Web dashboard (HTML) |
| `GET` | `/health` | `{"status": "ok"}` |
| `GET` | `/sysinfo` | Hostname, OS, CPU, RAM, boot time |
| `GET` | `/stats` | JSON array — all snapshots from the last 10 minutes |
| `GET` | `/stats/latest` | JSON object — most recent snapshot |

**Stop the server**

```bash
kill <PID>          # PID is printed when the server starts
```

**Web dashboard**

Open `http://127.0.0.1:8000/` in a browser to see a real-time charts dashboard that polls `/stats/latest` automatically.

---

### `minit stats`

Print a one-shot JSON snapshot of all system statistics to stdout.

```bash
minit stats              # compact JSON (suitable for piping)
minit stats --pretty     # indented JSON (human-readable)
```

**Options**

| Flag | Default | Description |
|---|---|---|
| `--pretty` | `false` | Pretty-print JSON with indentation |

**Example output (abbreviated)**

```json
{
  "timestamp": "2026-03-20T12:00:00+00:00",
  "cpu": {
    "overall_percent": 14.2,
    "per_core_percent": [12.5, 16.0, 10.1, 18.0],
    "count_logical": 4,
    "count_physical": 2,
    "freq_mhz": 2400
  },
  "memory": {
    "virtual": { "total_mb": 16384, "used_mb": 8192, "percent": 50.0 },
    "swap":    { "total_mb": 4096,  "used_mb": 512,  "percent": 12.5 }
  },
  "disk": { ... },
  "network": { ... },
  "processes": { ... }
}
```

**Scripting examples**

```bash
# Save a snapshot to a file
minit stats > snapshot.json

# Extract overall CPU % with jq
minit stats | jq '.cpu.overall_percent'

# Pipe into a monitoring script
while true; do minit stats; sleep 30; done | tee -a metrics.ndjson
```

---

### `minit setup`

Add the `minit` install directory to PATH so the command is available in every new shell session.

```bash
minit setup              # user-level
minit setup --system     # also add to system-wide PATH (requires sudo / admin)
```

**What it modifies**

| Platform | User-level | System-level |
|---|---|---|
| Linux / macOS | `~/.bashrc`, `~/.zshrc` | `/etc/environment` |
| Windows | `HKCU\Environment` via `setx` | `HKLM` environment key |

**Options**

| Flag | Default | Description |
|---|---|---|
| `--system` | `false` | Also write to system-wide PATH |

After running setup, restart your shell (or run `source ~/.bashrc`) for the change to take effect.

---

### `minit --version`

Print the installed version and exit.

```bash
minit --version
# minit 0.3.0
```

---

## Global flags

| Flag | Description |
|---|---|
| `--help` | Show help for any command |
| `--version` | Print version and exit |

Run `minit <command> --help` for command-specific help.

---

## Requirements

- Python 3.9 or later
- Ubuntu / Debian or Windows 10 / 11
- Dependencies installed automatically with pip: `psutil`, `rich`
