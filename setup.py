"""setuptools shim – legacy post-install PATH hook.

All package metadata lives in pyproject.toml.

NOTE: Modern pip (21.3+) builds a wheel via the build backend and installs it
by copying files, so it never calls `setup.py install`.  These PostInstall /
PostDevelop hooks therefore run only in legacy scenarios:
  - `python setup.py install`
  - `pip install --no-binary :all: minit-cli`
  - `pip install -e .`  (editable / develop mode)

For regular `pip install minit-cli` the PATH prompt is instead shown on the
first interactive invocation of the `minit` command itself.
"""
import os
import sys

from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install


def _run_path_setup() -> None:
    # Insert the project root so we can import from minit_cli even when this
    # script is executed from a temporary build directory by pip.
    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    try:
        from minit_cli._path_setup import add_to_path
        print("\nminit: configuring PATH …")
        add_to_path(system=False)
    except Exception as exc:
        # Never let a PATH-setup failure break the install.
        print(f"minit: PATH setup skipped ({exc})", file=sys.stderr)


class PostInstall(install):
    """Standard install + automatic PATH setup."""

    def run(self) -> None:
        super().run()
        _run_path_setup()


class PostDevelop(develop):
    """Editable install (`pip install -e .`) + automatic PATH setup."""

    def run(self) -> None:
        super().run()
        _run_path_setup()


setup(
    cmdclass={
        "install": PostInstall,
        "develop": PostDevelop,
    }
)
