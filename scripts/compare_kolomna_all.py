#!/usr/bin/env python3
"""Сравнение всех Kolomna-скриншотов: референс HTML vs PyQt."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.kolomna_compare_common import REF_DIR, APP_DIR, DIFF_DIR, compare_pair

THRESHOLD = 3.0  # % mean diff — цель pixel-perfect


def main() -> int:
    names = set()
    for d in (REF_DIR, APP_DIR):
        if d.is_dir():
            names.update(p.stem for p in d.glob("*.png"))
    names = sorted(names)

    results = []
    failed = []
    perfect = []
    for name in names:
        r = compare_pair(name)
        results.append(r)
        if "error" in r:
            print(f"SKIP {name}: {r['error']}")
            continue
        pct = r["diff_pct"]
        mark = "OK" if pct <= THRESHOLD else "FAIL"
        if pct == 0.0:
            perfect.append(name)
        print(f"{mark} {name}: {pct}%")
        if pct > THRESHOLD:
            failed.append(name)

    report = {
        "threshold": THRESHOLD,
        "results": results,
        "failed": failed,
        "perfect": perfect,
        "pass_rate": round(100 * (len(names) - len(failed)) / max(1, len(names)), 1),
    }
    out = DIFF_DIR / "report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nreport: {out}")
    print(f"failed: {len(failed)} / {len(names)}")
    print(f"perfect (0.0%): {len(perfect)} / {len(names)}")
    print(f"pass rate: {report['pass_rate']}%")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
