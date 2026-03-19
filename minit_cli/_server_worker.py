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

    from minit_cli.api.server import run_server
    run_server(host=args.host, port=args.port, interval=args.interval)


if __name__ == "__main__":
    main()
