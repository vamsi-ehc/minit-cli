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
minit dashboard
```

> **Requirements:** Python 3.9+ on Ubuntu/Debian or Windows 10/11.

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

---

## Publishing to PyPI

### Prerequisites

```bash
pip install build twine
```

### 1. Bump the version

Edit `pyproject.toml` and update the `version` field:

```toml
[project]
version = "0.2.0"   # increment as needed
```

### 2. Build the distribution

```bash
python -m build
```

This produces `dist/minit_cli-<version>-py3-none-any.whl` and `dist/minit_cli-<version>.tar.gz`.

### 3. Upload to PyPI

```bash
# Upload to the real PyPI index
twine upload dist/*
```

You will be prompted for your PyPI username and password (or an API token — recommended).
To use an API token, set your credentials once:

```bash
# ~/.pypirc  (create if it doesn't exist)
[pypi]
  username = __token__
  password = pypi-<your-api-token>
```

Or pass the token inline:

```bash
twine upload -u __token__ -p pypi-<your-api-token> dist/*
```

### 4. Test on TestPyPI first (optional but recommended)

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ minit-cli
```

### 5. Verify the published package

```bash
pip install minit-cli          # install from PyPI
minit --help
minit dashboard
```

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
