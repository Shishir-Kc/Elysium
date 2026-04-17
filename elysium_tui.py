#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════╗
║   ELYSIUM — Home Agent TUI Dashboard     ║
║   Run: uv run elysium_tui.py             ║
╚═══════════════════════════════════════════╝
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Elysium_Cli.Cli.cli import main

if __name__ == "__main__":
    main()
