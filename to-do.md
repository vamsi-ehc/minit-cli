# Roadmap

Items are ordered by dependency and complexity — earlier items unblock or lay groundwork for later ones.

---

## Phase 1 — Foundation & Configuration

- [ ] **Configuration File** — Manage `minit` settings (host, port, refresh interval, log path, retention) via a config file at a standard path (e.g. `~/.config/minit/config.toml`)
- [ ] **Config Command** — `minit config --path` to print the active config location; `minit config --show` to display current values; `minit config set <key> <value>` for quick edits
- [ ] **`minit stop` Command** — Gracefully stop a running `minit serve` server by PID; currently there is no built-in stop command
- [ ] **`minit status` Command** — Show whether the server is running, its PID, host/port, and uptime
- [ ] **Improved `minit stats` Output** — Add `--format` flag to support `json`, `table`, and `csv` output modes for easier scripting

---

## Phase 2 — Metrics Logging & History

- [ ] **Metrics Logging** — Persist snapshots to local log files (e.g. `~/.local/share/minit/logs/`) in JSON Lines format for easy parsing
- [ ] **Log Rotation** — Configurable retention via `--max-days N`; automatically delete logs older than N days on startup
- [ ] **`minit logs` Command** — View, tail (`--follow`), and filter (`--since`, `--until`) stored log files from the CLI
- [ ] **Extended History Window** — Make the in-memory rolling window duration configurable (currently hardcoded to 10 minutes)
- [ ] **Alerting / Thresholds** — Define CPU/RAM/Disk thresholds in config; log a warning or run a shell hook when a threshold is crossed

---

## Phase 3 — Additional Collectors

- [ ] **GPU Metrics** — Collect GPU utilization, VRAM usage, and temperature via `pynvml` (NVIDIA) with graceful fallback when no GPU is present
- [ ] **Temperature & Fan Sensors** — Expose CPU/motherboard temperatures and fan speeds via `psutil.sensors_temperatures()` and `psutil.sensors_fans()`
- [ ] **Battery Status** — Report charge level, charging state, and estimated time remaining on laptops
- [ ] **System Load Average** — Include 1/5/15-minute load averages in the snapshot (Linux/macOS)
- [ ] **Open Ports & Connections** — List active TCP/UDP connections and listening ports, visible in the dashboard and API

---

## Phase 4 — API & Security

- [ ] **API Authentication** — Protect the `/stats`, `/stats/latest`, and `/sysinfo` endpoints with an API key (passed via `Authorization: Bearer <key>` header); key stored in config
- [ ] **CORS Configuration** — Allow configurable allowed origins for cross-origin web dashboard access
- [ ] **TLS / HTTPS Support** — Accept a `--cert` and `--key` flag in `minit serve` to enable HTTPS via uvicorn's SSL support
- [ ] **Rate Limiting** — Prevent abuse of the HTTP API with configurable per-IP request limits
- [ ] **Webhook / Remote Export** — Push snapshots to a user-defined HTTP endpoint on each collection interval; configurable via config file

---

## Phase 5 — Storage Backends

- [ ] **SQLite Backend** — Optional persistent storage using SQLite; enables historical queries beyond the in-memory window
- [ ] **TimeSeries DB Support** — Optional integration with InfluxDB or Prometheus remote-write for long-term storage and external dashboards
- [ ] **`/stats/history` Endpoint** — Query historical data from the storage backend with `?from=` and `?to=` filters
- [ ] **Storage Management UI** — View, filter, and delete stored log data from the web dashboard

---

## Phase 6 — Web Dashboard Improvements

- [ ] **Dark/Light Theme Toggle** — Add a theme switcher to the web dashboard
- [ ] **Configurable Dashboard Layout** — Let users pin/reorder panels and choose which metrics are shown
- [ ] **Alert Banner** — Display a real-time alert in the web dashboard when a threshold is exceeded
- [ ] **Export from Dashboard** — Download current or historical metrics as CSV or JSON directly from the web UI
- [ ] **React + Vite Frontend** — Migrate the web UI from vanilla JS to React/Vite for better state management, component reuse, and testability; prerequisite for more complex UI features

---

## Phase 7 — Packaging & Ecosystem
add pyinstaller and create binaries
- [ ] **System Service Installation** — `minit install-service` generates and installs a `systemd` unit file (Linux) or Windows Service so the server starts on boot
- [ ] **Shell Completions** — Generate tab-completion scripts for bash, zsh, and fish via Click's built-in completion support
- [ ] **Docker Image** — Official `Dockerfile` and published image on Docker Hub / GHCR for containerized deployments
- [ ] **Project Website** — Public-facing site with feature overview, quick-start guide, and changelog
- [ ] **Hosted Documentation** — Structured docs (e.g. via MkDocs or Docusaurus) covering installation, configuration, API reference, and examples

---

## Phase 8 — Monetization

- [ ] **Multi-node Support** — Agent mode, multi-node dashboard, and node discovery/registry (paid feature)
- [ ] **Premium Tier** — Cloud aggregation, hosted dashboards, longer retention, team management; implement licensing/entitlement check
