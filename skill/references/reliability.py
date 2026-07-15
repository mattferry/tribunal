#!/usr/bin/env python3
"""Per-auditor reliability log — tribunal.

Every tribunal audit already produces the ground truth for free: you disposition
each finding CONFIRMED / REFUTED / UNCERTAIN yourself. This helper persists that
per auditor so a model's track record compounds across runs instead of being
thrown away. Over time you learn which auditor confirms often and which one
fabricates — and you spend your verification budget accordingly (scrutinize the
chronically-noisy model's findings first, weight a lone flag from it less).

The log is one JSON object per line at audits/reliability.jsonl (the audits/
dir is gitignored — reliability data embeds model/auditor names, keep it local).

    log:     append one run's tally for one auditor
    summary: print each auditor's running confirm-rate and fabrication-rate

Usage:
    python reliability.py log --auditor grok --model grok-4.5 \
        --findings 11 --confirmed 8 --refuted 3 --fabricated 3 --date 2026-07-14
    python reliability.py summary

"fabricated" is the subset of "refuted" that failed the existence pre-filter
(cited a nonexistent file/line) — track it separately; it is the failure mode
tribunal exists to catch.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

DEFAULT_LOG = "audits/reliability.jsonl"


def cmd_log(args: argparse.Namespace) -> int:
    rec = {
        "date": args.date,
        "auditor": args.auditor,
        "model": args.model,
        "findings": args.findings,
        "confirmed": args.confirmed,
        "refuted": args.refuted,
        "uncertain": args.uncertain,
        "fabricated": args.fabricated,
    }
    path = Path(args.file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    print(f"logged: {args.auditor} ({args.model}) "
          f"{args.confirmed}/{args.findings} confirmed, {args.fabricated} fabricated "
          f"-> {path}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.is_file():
        print(f"no log at {path} yet — run `log` first")
        return 0
    agg: dict[str, dict[str, int]] = defaultdict(
        lambda: {"runs": 0, "findings": 0, "confirmed": 0, "refuted": 0,
                 "uncertain": 0, "fabricated": 0})
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        a = agg[r.get("auditor", "?")]
        a["runs"] += 1
        for k in ("findings", "confirmed", "refuted", "uncertain", "fabricated"):
            a[k] += int(r.get(k, 0) or 0)

    print(f"{'auditor':16}  {'runs':>4}  {'finds':>5}  {'conf%':>6}  {'fab%':>6}")
    print("-" * 48)
    for name, a in sorted(agg.items()):
        f = a["findings"] or 1
        conf = 100.0 * a["confirmed"] / f
        fab = 100.0 * a["fabricated"] / f
        print(f"{name:16}  {a['runs']:>4}  {a['findings']:>5}  {conf:>5.0f}%  {fab:>5.0f}%")
    print("\nconf% = confirmed/findings (higher = more trustworthy); "
          "fab% = fabricated/findings (higher = scrutinize its citations harder).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="tribunal per-auditor reliability log")
    ap.add_argument("--file", default=DEFAULT_LOG, help=f"log path (default: {DEFAULT_LOG})")
    sub = ap.add_subparsers(dest="cmd", required=True)

    lg = sub.add_parser("log", help="append one auditor's tally for one run")
    lg.add_argument("--auditor", required=True)
    lg.add_argument("--model", default="")
    lg.add_argument("--date", default="", help="YYYY-MM-DD (caller supplies)")
    lg.add_argument("--findings", type=int, required=True)
    lg.add_argument("--confirmed", type=int, required=True)
    lg.add_argument("--refuted", type=int, default=0)
    lg.add_argument("--uncertain", type=int, default=0)
    lg.add_argument("--fabricated", type=int, default=0)
    lg.set_defaults(func=cmd_log)

    sm = sub.add_parser("summary", help="print running per-auditor stats")
    sm.set_defaults(func=cmd_summary)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
