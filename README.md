# minit-cli

A cross-platform (Ubuntu & Windows) real-time machine-stats CLI tool with a JSON export API.

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
| **JSON export API** | FastAPI server exposing last 10 minutes of snapshots at `GET /stats` |

---

## Install from PyPI

```bash
pip install minit-cli
minit setup          # adds minit to PATH (user shells + optionally system)
minit dashboard
```

> **Requirements:** Python 3.9+ on Ubuntu/Debian or Windows 10/11.

> **Note:** If `minit` is not found after install, modern pip does not run
> post-install hooks, so the PATH may not be updated automatically.
> Run the setup step via Python directly instead:
>
> ```bash
> python -m minit_cli.cli setup
> ```
>
> Then restart your shell (or run `source ~/.bashrc`) and `minit` will be available.

---

## Local setup

```bash
# 1. Clone the repo
git clone https://github.com/vamsi-ehc/minit-cli
cd minit-cli

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install the package in editable mode
pip install -e .

# 5. Verify the CLI is available
minit --help
```

### Run tests

```bash
pytest
```

---

## Commands

### `minit dashboard`

Launch the full-screen real-time terminal dashboard (press **Ctrl-C** to quit).

```
minit dashboard              # default: refresh every 2 s
minit dashboard --refresh 5  # refresh every 5 s
```

### `minit serve`

Start the JSON export API server.  Stats are collected in the background and kept
for 10 minutes (configurable via `--interval`).

```
minit serve                          # http://127.0.0.1:8000
minit serve --host 0.0.0.0 --port 9000 --interval 5
```

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness probe |
| `GET` | `/stats` | All snapshots from the last 10 minutes (JSON array) |
| `GET` | `/stats/latest` | Most recent snapshot (JSON object) |

Interactive API docs are available at `http://<host>:<port>/docs`.

### `minit stats`

Print a one-shot JSON snapshot to stdout (useful for scripting).

```
minit stats              # compact JSON
minit stats --pretty     # indented JSON
```

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

## Publishing to PyPI

Publishing is handled automatically by the GitHub Actions workflow on every
pushed tag.  To release a new version:

1. Bump `version` in `pyproject.toml`
2. Commit and push, then create a tag:

```bash
git tag v0.2.0
git push origin v0.2.0
```

The workflow builds and uploads the package to PyPI.

---

## Project layout

```
minit_cli/
  cli.py                  # Click CLI entry point
  collectors/
    cpu.py                # Per-core CPU stats (psutil)
    memory.py             # RAM + swap stats
    disk.py               # Disk space + I/O
    network.py            # Per-NIC network stats
    processes.py          # Top-N process list
  dashboard/
    live.py               # Rich live dashboard
  api/
    server.py             # FastAPI application
    store.py              # Thread-safe 10-min rolling buffer
tests/
  test_collectors.py
  test_store.py
  test_server.py
  test_cli.py
```
