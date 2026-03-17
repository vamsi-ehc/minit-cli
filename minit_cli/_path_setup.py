"""Shared logic for adding the minit bin directory to PATH.

Used by both setup.py (post-install hook) and the `minit setup` CLI command.
"""
from __future__ import annotations

import platform
import sys
from pathlib import Path


def bin_dir() -> str:
    return str(Path(sys.executable).parent)


def add_to_path(system: bool = False) -> None:
    if platform.system() == "Windows":
        _setup_windows(bin_dir(), system)
    else:
        _setup_unix(bin_dir(), system)


# ---------------------------------------------------------------------------
# Unix / Linux / macOS
# ---------------------------------------------------------------------------

def _setup_unix(d: str, system: bool) -> None:
    export = f'\nexport PATH="{d}:$PATH"  # added by minit\n'
    for rc in [Path.home() / ".bashrc", Path.home() / ".zshrc"]:
        try:
            existing = rc.read_text() if rc.exists() else ""
            if d not in existing:
                with rc.open("a") as fh:
                    fh.write(export)
                print(f"  [minit] added {d} to PATH in {rc}")
            else:
                print(f"  [minit] {d} already present in {rc}")
        except OSError as exc:
            print(f"  [minit] could not update {rc}: {exc}", file=sys.stderr)

    if system:
        _patch_etc_environment(d)
    else:
        print(
            "  [minit] run `minit setup --system` (with sudo) to also update"
            " /etc/environment for all users."
        )

    print("  [minit] restart your shell or run:  source ~/.bashrc")


def _patch_etc_environment(d: str) -> None:
    etc_env = Path("/etc/environment")
    try:
        existing = etc_env.read_text() if etc_env.exists() else ""
        if d in existing:
            print(f"  [minit] {d} already present in {etc_env}")
            return
        lines = existing.splitlines(keepends=True)
        new_lines: list[str] = []
        patched = False
        for line in lines:
            if line.startswith("PATH="):
                val = line[5:].strip().strip('"')
                new_lines.append(f'PATH="{d}:{val}"\n')
                patched = True
            else:
                new_lines.append(line)
        if not patched:
            new_lines.append(
                f'PATH="{d}:/usr/local/sbin:/usr/local/bin'
                ':/usr/sbin:/usr/bin:/sbin:/bin"\n'
            )
        etc_env.write_text("".join(new_lines))
        print(f"  [minit] added {d} to PATH in {etc_env}")
    except PermissionError:
        print(
            f"  [minit] permission denied writing {etc_env}."
            " Re-run with sudo: sudo minit setup --system",
            file=sys.stderr,
        )
    except OSError as exc:
        print(f"  [minit] could not update {etc_env}: {exc}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Windows
# ---------------------------------------------------------------------------

def _setup_windows(d: str, system: bool) -> None:
    import subprocess

    def _reg_path(machine: bool) -> str:
        import winreg  # type: ignore[import]
        root = winreg.HKEY_LOCAL_MACHINE if machine else winreg.HKEY_CURRENT_USER
        sub = (
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            if machine else r"Environment"
        )
        with winreg.OpenKey(root, sub) as key:
            value, _ = winreg.QueryValueEx(key, "PATH")
        return value

    scopes = [("user", [])]
    if system:
        scopes.append(("system", ["/M"]))

    for scope, flag in scopes:
        try:
            current = _reg_path(machine=(scope == "system"))
            if d.lower() in current.lower():
                print(f"  [minit] {d} already present in {scope} PATH")
                continue
            result = subprocess.run(
                ["setx", "PATH", f"{d};{current}"] + flag,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print(f"  [minit] added {d} to {scope} PATH via setx")
            else:
                print(
                    f"  [minit] setx failed for {scope} PATH:"
                    f" {result.stderr.strip()}",
                    file=sys.stderr,
                )
        except Exception as exc:  # pragma: no cover
            print(f"  [minit] {scope} PATH update failed: {exc}", file=sys.stderr)

    if not system:
        print(
            "  [minit] run `minit setup --system` from an admin shell to"
            " also update the system PATH."
        )
    print("  [minit] restart your terminal for the PATH change to take effect.")
