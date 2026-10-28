"""Entrypoint: `python -m react_agent`."""

from __future__ import annotations

from react_agent import __version__
from react_agent.configuration import settings


def main() -> None:
    header = f"React Agent v{__version__}"
    status = f"environment={settings.environment}, seed={settings.seed}"
    print(f"{header} - {status}")


if __name__ == "__main__":
    main()
