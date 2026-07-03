"""Entry point.

  python -m zk_gchat_mcp          -> start de stdio MCP-server (voor Claude Code)
  python -m zk_gchat_mcp setup    -> eenmalige OAuth browser-login
"""
from __future__ import annotations

import sys


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        from .auth import run_setup
        return run_setup()
    from .server import run
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
