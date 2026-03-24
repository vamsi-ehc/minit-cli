# minit-cli

<div align="center">
  <img src="landing/assets/logo.svg" alt="minit logo" width="80" height="80" />
</div>

A cross-platform (Ubuntu & Windows) real-time machine-stats CLI tool with a JSON export API, persistent metric logging, and configurable alerting.

[![PyPI](https://img.shields.io/pypi/v/minit-cli)](https://pypi.org/project/minit-cli/)
[![Python](https://img.shields.io/pypi/pyversions/minit-cli)](https://pypi.org/project/minit-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

| Feature | Details |
|---|---|
| Per-core CPU | Usage % for every logical core + overall average, physical/logical count, frequency |
| Memory | Virtual RAM and swap utilisation (MB, %) |
| Disk space | Per-partition used/free/total (GB, %) for all mounted filesystems |
| Disk I/O | Cumulative read/write bytes and operation counts per disk |
| Network | Per-NIC bytes sent/received, packet counts, errors and drops |
| Process list | Top-N processes sorted by CPU %, with PID, name, user, status, CPU%, Mem% |
| **Real-time dashboard** | Full-screen terminal dashboard via `rich`, refreshed every 2 s |
| **JSON export API** | HTTP server exposing a configurable rolling window of snapshots at `GET /stats` |
| **Persistent logging** | Snapshots written to daily `.jsonl` files; configurable retention |
| **Threshold alerting** | Configurable CPU/RAM/disk alerts logged to `alerts.jsonl` + optional shell hook |
| **Config file** | All defaults managed via `~/.config/minit/config.toml` |

---

## Install from PyPI

```bash
pip install minit-cli
minit setup          # adds minit to PATH (user shells + optionally system)
minit dashboard
```

> **Requirements:** Python 3.9+ on Ubuntu/Debian or Windows 10/11.

---

### "minit: command not found" / "'minit' is not recognized"

pip installs CLI scripts into a **scripts directory** that may not be on your
PATH yet.  Follow the steps for your OS below.

#### Windows

1. Find the scripts directory:
   ```
   python -m site --user-site
   ```
   Replace `site-packages` at the end of that path with `Scripts`, e.g.
   `C:\Users\<you>\AppData\Roaming\Python\Python312\Scripts`

   Or run this one-liner to print the exact path:
   ```powershell
   python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
   ```

2. Add that path to your **system** (or user) environment variable:

   **GUI** — Search → "Edit the system environment variables" → *Environment
   Variables* → select **Path** under *User variables* → *Edit* → *New* →
   paste the Scripts path → OK.

   **PowerShell (one-liner)**:
   ```powershell
   [System.Environment]::SetEnvironmentVariable(
       "PATH",
       [System.Environment]::GetEnvironmentVariable("PATH","User") + ";C:\Users\<you>\AppData\Roaming\Python\Python312\Scripts",
       "User"
   )
   ```

3. **Close and reopen** your terminal, then run `minit --help`.

> **Tip:** If you installed into a virtual environment, activate it first
> (`.venv\Scripts\activate`) — the `minit` command will be available
> automatically while the venv is active.

---

#### Linux / macOS

1. Find the scripts directory:
   ```bash
   python3 -m site --user-base
   ```
   The scripts live in `<user-base>/bin`, e.g. `~/.local/bin`.

2. Check whether that directory is already on your PATH:
   ```bash
   echo $PATH | tr ':' '\n' | grep -i local
   ```

3. If it is **not** listed, add it to your shell profile:

   **bash** — append to `~/.bashrc`:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

   **zsh** — append to `~/.zshrc`:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

   **fish** — run once:
   ```fish
   fish_add_path ~/.local/bin
   ```

4. Verify:
   ```bash
   which minit
   minit --help
   ```

> **Virtual environment:** If you installed inside a venv, activate it first:
> ```bash
> source .venv/bin/activate
> ```
> The `minit` command is available as long as the venv is active.

---

#### Alternative — run via Python directly (all platforms)

If you prefer not to modify PATH, invoke the CLI through the Python interpreter:

```bash
python -m minit_cli.cli dashboard
python -m minit_cli.cli serve
python -m minit_cli.cli stats
```

---

## Commands

### `minit dashboard`

Launch the full-screen real-time terminal dashboard (press **Ctrl-C** to quit).

```
minit dashboard              # default: refresh every 2 s (or from config)
minit dashboard --refresh 5  # refresh every 5 s
```

---

### `minit serve`

Start the JSON export API server in the background. Snapshots are collected on a
configurable interval, kept in a rolling in-memory window, and also written to
daily log files on disk.

```
minit serve                                          # defaults from config
minit serve --host 0.0.0.0 --port 9000
minit serve --interval 5 --window 1800              # 5 s interval, 30 min window
```

| Flag | Default | Description |
|---|---|---|
| `--host` | `127.0.0.1` | Bind host |
| `--port` | `8000` | Bind port |
| `--interval` | `10` | Collection interval (seconds) |
| `--window` | `600` | In-memory rolling window (seconds) |

All flags fall back to values in `~/.config/minit/config.toml` when not specified.

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Web dashboard |
| `GET` | `/health` | Liveness probe |
| `GET` | `/stats` | All snapshots in the rolling window (JSON array) |
| `GET` | `/stats/latest` | Most recent snapshot (JSON object) |
| `GET` | `/sysinfo` | Static system information |

---

### `minit stop`

Stop the running background server.

```
minit stop
```

---

### `minit status`

Show whether the server is running, plus its PID, host, port, and uptime.

```
minit status
```

```
minit server: running
  PID:     12345
  host:    127.0.0.1
  port:    8000
  uptime:  00:42:17
```

---

### `minit stats`

Print a one-shot snapshot to stdout (useful for scripting).

```
minit stats                      # compact JSON
minit stats --pretty             # indented JSON
minit stats --format table       # aligned key/value table
minit stats --format csv         # two-column CSV
```

---

### `minit logs`

View, filter, or tail the persistent metric log files stored in
`~/.local/share/minit/logs/` (one `.jsonl` file per day).

```
minit logs                          # all entries from today
minit logs --date 2024-01-15        # entries for a specific date
minit logs --since 1h               # last hour
minit logs --since 30m              # last 30 minutes
minit logs --since 2024-01-15T10:00 # from an absolute timestamp
minit logs --until 2024-01-15T12:00 # up to a timestamp
minit logs --follow                 # tail live (Ctrl-C to stop)
minit logs --pretty                 # pretty-print JSON
```

Alert events are stored separately in `alerts.jsonl` in the same directory.

---

### `minit config`

Manage the configuration file at `~/.config/minit/config.toml`.

```
minit config                          # show all current values
minit config --show                   # same as above
minit config --path                   # print the config file path

minit config set server.port 9000
minit config set server.interval 5
minit config set server.history_window 1800
minit config set dashboard.refresh 1.0
minit config set logging.retention_days 30
minit config set thresholds.cpu_percent 85
minit config set thresholds.memory_percent 90
minit config set thresholds.disk_percent 80
minit config set thresholds.hook "notify-send minit '$MINIT_ALERT_METRIC exceeded'"
```

**Config keys:**

| Key | Default | Description |
|---|---|---|
| `server.host` | `127.0.0.1` | API server bind host |
| `server.port` | `8000` | API server bind port |
| `server.interval` | `10` | Collection interval (seconds) |
| `server.history_window` | `600` | In-memory rolling window (seconds) |
| `dashboard.refresh` | `2.0` | Terminal dashboard refresh interval |
| `logging.log_path` | `~/.local/share/minit/logs` | Directory for `.jsonl` log files |
| `logging.retention_days` | `7` | Days to keep daily log files |
| `thresholds.cpu_percent` | `-1` | Alert when CPU % ≥ value (`-1` = disabled) |
| `thresholds.memory_percent` | `-1` | Alert when RAM % ≥ value (`-1` = disabled) |
| `thresholds.disk_percent` | `-1` | Alert when any disk % ≥ value (`-1` = disabled) |
| `thresholds.hook` | `""` | Shell command to run on alert (empty = disabled) |

**Alert hook environment variables:**

| Variable | Description |
|---|---|
| `MINIT_ALERT_METRIC` | Metric name (`cpu_percent`, `memory_percent`, `disk_percent`) |
| `MINIT_ALERT_VALUE` | Observed value |
| `MINIT_ALERT_THRESHOLD` | Configured threshold |
| `MINIT_ALERT_TIMESTAMP` | ISO 8601 timestamp |
| `MINIT_ALERT_MOUNTPOINT` | Mount point (disk alerts only) |

---

### `minit setup`

Add the `minit` install directory to PATH so the command is available in every
new shell session.

```
minit setup              # user-level: ~/.bashrc and ~/.zshrc (Linux/macOS)
                         #             HKCU\Environment via setx (Windows)
minit setup --system     # also update system-wide PATH
                         # Linux/macOS: /etc/environment (requires sudo)
                         # Windows:     HKLM environment key (requires admin shell)
```

---

## Development setup

> For contributors and anyone who wants to run or modify the source directly.

### Prerequisites

- Python 3.9 or newer
- `git`

### 1. Clone the repository

```bash
git clone https://github.com/vamsi-ehc/minit-cli
cd minit-cli
```

### 2. Create and activate a virtual environment

```bash
# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies and the package in editable mode

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Verify

```bash
minit --help
```

### Run tests

```bash
pytest
```
