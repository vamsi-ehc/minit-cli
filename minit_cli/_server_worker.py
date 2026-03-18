"""Background worker launched by `minit serve`.

Run as: python -m minit_cli._server_worker --host ... --port ... --interval ...
"""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args()

    import uvicorn
    from minit_cli.api.server import app, start_collector

    start_collector(interval=args.interval)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
