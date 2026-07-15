# Deterministic scanners as a read-only QA auditor

Every other auditor on the panel is an LLM, so every seat shares one failure mode: it
**hallucinates** findings. A deterministic static analyzer is the panel seat whose error profile
is the mirror image — it **never invents a finding** (a rule matched a real `file:line` or it
didn't), it is **100% reproducible**, it is **free and local** (no tokens, no rate limits, **no
egress**), and it emits **SARIF** for interop. It is your cheapest, always-on baseline, and the
one seat that decorrelates a panel that is otherwise all-LLM. Its weakness is the exact inverse of
the LLM's: it only finds *known patterns* and misses anything that needs understanding intent
(logic errors, broken business rules, subtle races). That is why it is a **complement**, not a
replacement: run at least one deterministic seat *and* at least one LLM auditor on any
security- or money-touching gate.

Tool behavior verified natively on Windows 2026-07-14: Bandit 1.9.4, ruff 0.15.21. Record the
exact invocations for your machine in `roster.md`.

## Standing state

- **Cage: read-only by construction.** A scanner only reads files and prints results; there is no
  edit or shell capability to disable. No `--sandbox`/`--tools` flag is needed — the read-only
  guarantee is the tool, not a flag. Say so in the report ("deterministic scanner — reads only").
- **Confidentiality: none leaves the machine.** These run entirely locally. This is the panel seat
  you can point at code you cannot send to a cloud provider.
- **Tools and coverage** (all free; all emit SARIF 2.1.0 unless noted):
  - **Bandit** — Python security (SQLi patterns, `eval`/`exec`, weak crypto, hardcoded secrets,
    `try/except/pass`). `pip install "bandit[sarif]"`. Native everywhere.
  - **ruff** — very fast Python linter; the `S` rule group is a Bandit reimplementation, `B` is
    bugbear (likely-bug patterns). `pip install ruff`. Native everywhere.
  - **Semgrep** — multi-language SAST, 2,800+ OWASP/CWE community rules. `pip install semgrep`.
    **Officially Linux/macOS**; on Windows run under WSL or Docker (`returntocorp/semgrep`).
  - **Gitleaks** — secret scanning over files and full git history (Go binary; Windows build
    available). Pair with **TruffleHog** for live-verified secrets (no native SARIF — JSON only).
  - **Trivy** — dependency CVEs, SBOMs, IaC misconfig, secrets (Go binary).

## Canonical audit invocation

```bash
mkdir -p audits

# Python security — Bandit, SARIF receipt:
bandit -r <DIR_TO_AUDIT> -f sarif -o audits/bandit.sarif
#   (Windows / this machine: `python -m bandit ...` — the console script may not be on PATH.)

# Python linter — ruff, security + bugbear groups, SARIF receipt:
ruff check <DIR_TO_AUDIT> --select S,B --output-format sarif -o audits/ruff.sarif
#   (Windows / this machine: `python -m ruff check ...`.)

# Multi-language (Linux/macOS/WSL/Docker):
semgrep --config auto --sarif -o audits/semgrep.sarif <DIR_TO_AUDIT>

# Secrets:
gitleaks detect --source <DIR_TO_AUDIT> --report-format sarif --report-path audits/gitleaks.sarif
```

The SARIF file *is* this auditor's receipt — save it under the ignored `audits/` dir like any
other. Each `result` carries `ruleId`, `level`, and a `physicalLocation` (`file` + `region`), so
every finding is already in `{file, line, severity, summary}` shape for your triage table.

## Feeding it into triage

- **Its citations always exist** — a scanner reports real `file:line`s, so its findings **skip the
  existence pre-filter** (`references/check_findings.py`); there is nothing to hallucinate.
- **But a pattern match is not automatically a confirmed defect.** Static analyzers are
  high-precision, not perfect: a flagged pattern can be safe in context (e.g. an `S608` SQL string
  with no attacker-reachable input). Deterministic removes *hallucination*, not the need for your
  judgment on **exploitability in context**. Disposition each scanner finding like any other —
  CONFIRMED / REFUTED (safe here, why) / UNCERTAIN — just skip the "does this line even exist" step.
- **Overlap with an LLM seat is strong corroboration.** When the scanner and an LLM auditor both
  flag the same line (e.g. both catch the f-string SQL), that is a near-certain real defect — the
  agreement crosses the LLM/deterministic boundary, the widest decorrelation you can get.

## Never

- Never treat an empty scanner result as "clean." It only knows its rule set; the semantic defects
  it structurally cannot see (logic, races, intent) are exactly what the LLM seats are for.
- Never count two scanners of the same rule family (Bandit and ruff `--select S`) as two
  *independent* seats — they reimplement the same checks. For diversity, pair a scanner with an
  LLM auditor, or add a different-language/-class scanner (Semgrep, Gitleaks).
- Never paste a scanner's raw SARIF into the report as the whole deliverable — it is one seat's
  input to your triage, not the verdict.
