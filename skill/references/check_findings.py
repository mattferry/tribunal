#!/usr/bin/env python3
"""Mechanical existence pre-filter for auditor findings — tribunal.

Auditors hallucinate: they cite functions that don't exist and line numbers
past a file's end. Those are refutable *mechanically*, before you spend a single
semantic verification pass. This is the skill's "compare each cited line number
against the file's actual length before anything else" tell, automated.

Input: a findings JSON in the tribunal schema
    {"findings": [{"file": "...", "line": N, "severity": "...", "summary": "..."}]}
(pass a path with --findings, or pipe it on stdin). --base is the directory the
auditor read (file paths are resolved relative to it; a bare basename is also
matched anywhere in the tree).

Output: each finding tagged
    PASS   — file exists and the cited line is in range → still needs your
             semantic verification; this filter does NOT confirm it.
    REFUTE — file absent, or line past EOF / < 1 → a hallucinated citation.
             Auto-refute it; do not spend a verification pass on fiction.
    CHECK  — no usable file/line to test (e.g. line 0/None) → verify by hand.

Exit code is always 0 — this is triage input, not a gate. A nonzero count of
REFUTE rows is printed to stderr so a caller can notice.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load(findings_arg: str | None) -> list[dict]:
    raw = Path(findings_arg).read_text(encoding="utf-8") if findings_arg else sys.stdin.read()
    doc = json.loads(raw)
    if isinstance(doc, dict) and "findings" in doc:
        return doc["findings"]
    if isinstance(doc, list):
        return doc
    raise SystemExit("findings JSON must be a list or an object with a 'findings' key")


def _resolve(base: Path, cited: str) -> Path | None:
    """Best-effort locate the cited file under base."""
    if not cited:
        return None
    direct = (base / cited).resolve()
    if direct.is_file():
        return direct
    # fall back to matching the bare filename anywhere under base
    name = Path(cited).name
    matches = [p for p in base.rglob(name) if p.is_file()]
    return matches[0] if len(matches) == 1 else None


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as fh:
        return sum(1 for _ in fh)


def check(findings: list[dict], base: Path) -> list[dict]:
    rows = []
    for i, f in enumerate(findings, 1):
        cited_file = str(f.get("file", "") or "")
        line = f.get("line")
        summary = str(f.get("summary", "") or "")[:80]
        path = _resolve(base, cited_file)
        if path is None:
            verdict, why = ("REFUTE", f"file not found: {cited_file!r}")
        elif not isinstance(line, int) or line == 0:
            verdict, why = ("CHECK", "no usable line number")
        else:
            n = _line_count(path)
            if line < 1 or line > n:
                verdict, why = ("REFUTE", f"line {line} past EOF (file is {n} lines)")
            else:
                verdict, why = ("PASS", f"exists (file is {n} lines)")
        rows.append({"n": i, "file": cited_file, "line": line,
                     "verdict": verdict, "why": why, "summary": summary})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Existence pre-filter for tribunal findings")
    ap.add_argument("--findings", help="path to findings JSON (default: stdin)")
    ap.add_argument("--base", default=".", help="directory the auditor read (default: .)")
    ap.add_argument("--json", action="store_true", help="emit rows as JSON instead of a table")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    rows = check(_load(args.findings), base)

    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        print(f"{'#':>3}  {'VERDICT':7}  {'FILE:LINE':28}  WHY")
        print("-" * 88)
        for r in rows:
            loc = f"{r['file']}:{r['line']}"
            print(f"{r['n']:>3}  {r['verdict']:7}  {loc:28}  {r['why']}")

    refuted = sum(1 for r in rows if r["verdict"] == "REFUTE")
    passed = sum(1 for r in rows if r["verdict"] == "PASS")
    checkn = sum(1 for r in rows if r["verdict"] == "CHECK")
    print(f"\n{len(rows)} findings: {passed} exist (verify), "
          f"{refuted} hallucinated citations (auto-refute), {checkn} need a manual line check",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
