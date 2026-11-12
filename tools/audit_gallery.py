#!/usr/bin/env python3
"""Count visual defects across every example diagram.

    uv run python tools/audit_gallery.py            # print the table
    uv run python tools/audit_gallery.py --check    # fail if any count rose
    uv run python tools/audit_gallery.py --update   # record current counts

The baseline is a ratchet: counts may only go down. After fixing defects, run
``--update`` so the lower numbers become the new ceiling.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import warnings
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from diagrams_as_code.audit import DEFECTS, audit_diagram  # noqa: E402

BASELINE = REPO / "tools" / "audit_baseline.json"


def example_scripts() -> list[Path]:
    return sorted(REPO.glob("examples/*/*.py")) + sorted(REPO.glob("examples/[0-9]*.py"))


def load_diagram(path: Path):
    spec = importlib.util.spec_from_file_location(f"_audit_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.diagram()


def run() -> tuple[Counter, Counter, dict[str, Counter]]:
    """(total defects, diagrams affected per defect, per-script counts)."""
    total: Counter = Counter()
    affected: Counter = Counter()
    per_script: dict[str, Counter] = {}
    for script in example_scripts():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            counts = audit_diagram(load_diagram(script))
        per_script[str(script.relative_to(REPO))] = counts
        total.update(counts)
        affected.update(counts.keys())
    return total, affected, per_script


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if a count exceeds the baseline")
    parser.add_argument("--update", action="store_true", help="write current counts as the baseline")
    parser.add_argument("--verbose", action="store_true", help="list defects per script")
    args = parser.parse_args(argv)

    total, affected, per_script = run()
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
    print(f"{len(per_script)} diagrams")
    print(f"{'defect':28s} {'count':>6s} {'diagrams':>9s} {'baseline':>9s}")
    for name in DEFECTS:
        print(f"{name:28s} {total[name]:6d} {affected[name]:9d} {baseline.get(name, '-')!s:>9s}")
    if args.verbose:
        for script, counts in per_script.items():
            if counts:
                print(script, dict(counts))

    if args.update:
        BASELINE.write_text(json.dumps({n: total[n] for n in DEFECTS}, indent=2) + "\n")
        print(f"baseline written to {BASELINE.relative_to(REPO)}")
        return 0
    if args.check:
        worse = {n: (total[n], baseline.get(n, 0)) for n in DEFECTS if total[n] > baseline.get(n, 0)}
        if worse:
            for name, (now, was) in worse.items():
                print(f"REGRESSION {name}: {now} > baseline {was}", file=sys.stderr)
            return 1
        better = [n for n in DEFECTS if total[n] < baseline.get(n, 0)]
        if better:
            print("improved: " + ", ".join(better) + " (run --update to lock in)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
