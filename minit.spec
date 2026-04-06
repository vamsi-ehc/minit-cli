# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for minit-cli
#
# Build:
#   pip install pyinstaller
#   pyinstaller minit.spec
#
# Output:  dist/minit   (Linux/macOS)
#          dist\minit.exe  (Windows)
#
# NOTE: The `minit serve` command spawns a background process using
#   sys.executable + "-m minit_cli._server_worker"
# In a frozen binary sys.executable points to the minit binary itself,
# not to a Python interpreter, so that flag-based launch will not work.
# The server worker is therefore bundled as a *second* one-file executable
# (minit-server-worker) and the frozen CLI detects this and calls it instead.
# If you only need `dashboard` / `stats` / `setup`, you can remove the
# WORKER block below and ignore the serve command.

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# ── Hidden imports ────────────────────────────────────────────────────────────
hidden_imports = (
    collect_submodules("minit_cli")
    + collect_submodules("psutil")
    + collect_submodules("rich")
    + [
        # stdlib modules that PyInstaller may miss when they are imported
        # dynamically at runtime
        "http.server",
        "threading",
        "subprocess",
        "argparse",
        "json",
        "datetime",
        "pathlib",
        "platform",
        # psutil platform shims
        "psutil._pslinux",
        "psutil._psposix",
        "psutil._pswindows",
        "psutil._psosx",
    ]
)

# ── Data files ────────────────────────────────────────────────────────────────
# rich ships Markdown/theme data that must travel with the binary.
datas = collect_data_files("rich")

# ── Main CLI binary ───────────────────────────────────────────────────────────
cli_analysis = Analysis(
    ["minit_cli/cli.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "pytest", "doctest"],
    noarchive=False,
)

cli_pyz = PYZ(cli_analysis.pure)

cli_exe = EXE(
    cli_pyz,
    cli_analysis.scripts,
    cli_analysis.binaries,
    cli_analysis.datas,
    [],
    name="minit",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ── Server worker binary (needed for `minit serve`) ───────────────────────────
worker_analysis = Analysis(
    ["minit_cli/_server_worker.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "pytest", "doctest"],
    noarchive=False,
)

worker_pyz = PYZ(worker_analysis.pure)

worker_exe = EXE(
    worker_pyz,
    worker_analysis.scripts,
    worker_analysis.binaries,
    worker_analysis.datas,
    [],
    name="minit-server-worker",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
