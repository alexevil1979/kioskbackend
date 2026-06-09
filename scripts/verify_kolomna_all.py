#!/usr/bin/env python3
"""Полная верификация Kolomna UI: ref → grab → compare (цель 100%, порог ≤3%)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
THRESHOLD = 3.0

STEPS = (
    ("render ref", ROOT / "scripts" / "render_kolomna_reference.py"),
    ("grab app", ROOT / "scripts" / "grab_all_kolomna_screens.py"),
    ("compare screens", ROOT / "scripts" / "compare_kolomna_all.py"),
    ("compare categories zones", ROOT / "scripts" / "compare_categories_elements.py"),
)


def _run(script: Path) -> int:
    print(f"\n>>> {script.name}")
    return subprocess.call([PY, str(script)], cwd=str(ROOT))


def main() -> int:
    for label, script in STEPS:
        if not script.is_file():
            print(f"MISSING {script}", file=sys.stderr)
            return 1
        code = _run(script)
        if code != 0:
            print(f"\nFAIL at step: {label} (exit {code})", file=sys.stderr)
            return code

    import json

    report_path = ROOT / "logs" / "kolomna_diff" / "report.json"
    if not report_path.is_file():
        print("missing report.json", file=sys.stderr)
        return 1
    report = json.loads(report_path.read_text(encoding="utf-8"))
    failed = report.get("failed") or []
    perfect = report.get("perfect") or []
    total_screens = len(report.get("results") or [])

    print("\n=== Kolomna verify summary ===")
    print(f"screens: {total_screens - len(failed)}/{total_screens} pass (threshold {THRESHOLD}%)")
    print(f"screens perfect (0.0%): {len(perfect)}/{total_screens}")
    print(f"screens pass rate: {report.get('pass_rate', 0)}%")

    if failed:
        print(f"FAILED screens: {', '.join(failed)}", file=sys.stderr)
        return 1

    # 8 зон категорий уже проверены compare_categories_elements (exit 0)
    total_items = total_screens + 8
    print(f"categories zones: 8/8 pass")
    print(f"TOTAL: {total_items}/{total_items} items — 100%")
    print("ALL OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
