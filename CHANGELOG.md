# Changelog

All notable changes to `tribunal` are documented here. Versions before 1.0 are pre-stable; the
skill's own behavioral revisions are labeled inline in `skill/SKILL.md` (its provenance line) and
tracked in `testing/briefs.md`.

## [0.5.0] — 2026-07-15

First tagged release. `tribunal` is a Claude Code skill plus runbooks that convene external
coding agents as **read-only** QA auditors and triage their findings against the code with
receipts, instead of relaying them as truth.

### Added — decorrelating an all-LLM panel

- **Deterministic scanner seat** (`skill/references/static-analysis.md`) — Bandit / ruff /
  Semgrep as a first-class panel member. Free, local (no egress), reproducible, and it never
  hallucinates a citation: the mirror-image error profile of an LLM auditor, and the one seat
  that genuinely decorrelates an otherwise all-LLM panel. Emits SARIF; findings fold into triage
  as ground truth (still judged for exploitability in context).
- **Mechanical existence pre-filter** (`skill/references/check_findings.py`) — auto-refutes any
  auditor finding whose cited file is absent or whose line is past end-of-file, *before* a
  semantic verification pass. Turns the most common LLM auditor failure (fabricated file/line
  citations) into a deterministic reject.
- **Per-auditor reliability log** (`skill/references/reliability.py`) — appends each run's
  confirmed / refuted / uncertain / fabricated tally to `audits/reliability.jsonl` and reports a
  running confirm and fabrication rate per model, so a chronically unreliable seat is visible.
- **Cursor CLI auditor** (`skill/references/cursor.md`) — `cursor-agent --mode plan` as a
  structurally read-only seat (no edits, no shell). Recommended model `composer-2.5` adds a
  family distinct from both the orchestrator (Claude) and the Grok seat.

### Verified

- Iron-Law RED/GREEN behavioral testing on real Claude Opus 4.8 arms, five rounds. Round 5
  (skill v5) forensically passed **both** the single-auditor and the panel scenarios against
  nine PASS criteria — independent judges re-ran the helper scripts and the exploit repros, and
  confirmed each auditor's cage from its own session logs. The panel scenario is the sharpest
  data point: the LLM auditor fabricated half its findings (guessing blind, zero file reads), and
  the existence pre-filter caught the line-past-EOF citation mechanically. Corpus:
  `testing/green-results.md`; methodology and criteria: `testing/briefs.md`.

### Notes

- The core contract predates this release and was hardened across skill revisions v2–v5: four
  receipts per auditor (it ran, it was structurally caged, every finding was verified, cost and
  availability were named), union-disposition triage across a panel, and read-only enforced by
  flags rather than by prompt politeness.
- "Read-only" is a write cage, not a confidentiality guarantee — a cloud auditor transmits every
  file it reads. Use the local or deterministic seats for code you can't share externally.
- Codex remains a supported auditor but is documented as a standing gap on the reference machine
  (quota-blocked); the panel it was validated against is Grok + Cursor + the deterministic scanner.

[0.5.0]: https://github.com/mattferry/tribunal/releases/tag/v0.5.0
