#!/usr/bin/env python3
"""Ref vs app admin panel — делегирует verify (всегда генерирует compare PNG)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, str(ROOT / "scripts" / "verify_admin_panel.py")]))
