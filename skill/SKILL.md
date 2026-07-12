---
name: crosscheck
description: Use when running or triaging any external coding agent (Grok Build, Codex, a local model endpoint) as a reviewer or QA auditor of code — when Matt asks for a second opinion, external QA, or an independent audit of work, and before reporting externally-audited code as reviewed or ship-ready.
---

# crosscheck — external coding agents as your QA panel

You wrote the code, so you share every assumption that produced its bugs. An auditor from a
different model family (xAI's Grok, OpenAI's Codex, a local Qwen) breaks that correlation —
that is the entire value, and it survives only if the auditor is genuinely independent and the
audit is genuinely proven. Roles are fixed: **external agents audit, read-only; you (the
session) verify their findings, apply fixes, and own the report.** An auditor's word is never
quoted as a conclusion, and an auditor never touches the tree.

## The four receipts — PER AUDITOR, every one, no exceptions

These apply to **each panel member separately**. Receipting your headline auditor and
narrating the second one from memory is the exact failure a GREEN arm shipped: it proved Grok
and then wrote "DGX Qwen returned 7 findings" with no call, no output, no file. Half a
receipted panel is a half-faked panel.

1. **It ran.** The exact invocation and its raw or structured output appear in the report, or
   in a saved file whose path is given (one file per auditor is fine). An audit narrated from
   memory scores as **not-run — even when it really ran**. Proof is part of the work.
2. **It was caged.** Read-only enforcement is a **flag, not a vibe**: Grok
   `--tools "read_file,grep,list_dir"`; Codex `--sandbox read-only`; a chat endpoint is
   read-only by construction (it never sees the tree). A prompt sentence like "do not modify
   any files" is a request to a write-capable agent, not a control — and `--permission-mode
   auto`/`--always-approve` on an auditor is the opposite of a control. Never write "read-only"
   in a report unless the shown command proves it.
3. **You verified it.** Every finding gets a disposition **you** produced by reading the actual
   code — CONFIRMED (line + reason), REFUTED (reason), or UNCERTAIN (what would settle it).
   Show the decisive evidence for ship-blockers; better, *run* the bug (a three-line repro that
   prints `100 → 150` beats any amount of prose). "I verified each against the code" with
   nothing shown is an assertion, not verification.
4. **Costs and gaps are named**, per auditor, as a line in the report — e.g. "Grok: 1 call
   (Matt's grok.com sub) · DGX Qwen: 2 calls (free/local) · Codex: did not run — `codex login
   status` = not logged in." A silently shrunken panel is a faked panel; an unpriced panel
   hides what it spent.

**Auditors hallucinate — that is why you verify.** A GREEN arm caught Grok inventing 6 of 15
findings: a `cancel()` function that doesn't exist, a `product_id` query, line numbers 42–82 in
a 26-line file. It threw them out and said so. That is the skill working. Relaying an
auditor's findings unverified doesn't just risk noise, it risks reporting fiction as fact.

## Panel roster (mattpc — verified 2026-07-12; full runbooks in `references/`)

| Auditor | Invoke | Auth / cost | Read-only flag | Notes |
|---|---|---|---|---|
| **Grok Build** (grok-4.5) | `grok.exe` headless `-p` | grok.com OAuth on disk / Matt's xAI sub | `--tools "read_file,grep,list_dir"` | `--json-schema` → parse `structuredOutput`. [references/grok.md](references/grok.md) |
| **Codex CLI** (OpenAI) | `codex exec` | **unauth'd as of 2026-07-12** — needs `codex login` or `OPENAI_API_KEY` | `--sandbox read-only` (OS-level) | `codex exec review` is purpose-built; `--output-schema <file>`. [references/codex.md](references/codex.md) |
| **DGX Qwen3-Coder-30B** | POST `http://100.95.10.94:8000/v1/chat/completions` | none / free | API-only, sees only what you send | ~7s per file; scoped view — per-file findings only. [references/local-openai.md](references/local-openai.md) |

Re-verify availability before claiming a member ran or is down: `grok models` (says "logged
in"), `codex login status`, `GET /v1/models` on the DGX.

## Canonical Grok audit (the one you'll use most)

```powershell
grok --cwd <DIR> -p "<what to read, what to look for>" `
  --tools "read_file,grep,list_dir" --max-turns 12 `
  --json-schema '{"type":"object","properties":{"findings":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string"},"summary":{"type":"string"}},"required":["file","line","severity","summary"]}}},"required":["findings"]}'
```

Parse `structuredOutput.findings`. Keep the prompt you sent — the report quotes it exactly or
not at all (baseline paraphrased its own prompt as a fake quote).

## Panel sizing

| Situation | Panel |
|---|---|
| Routine diff, low blast radius | 1 auditor (cheapest available) |
| Ship-gate on product code | 2 auditors, different families |
| Security-sensitive / money / prod-touching | 2+, each prompted with a different lens (correctness, security, concurrency) |
| A member unavailable | Run the rest, report the gap |

Dissent is signal: agreement across families ≈ near-confirmed (verify fast, fix); a unique
finding is normal (silence of other auditors is not exoneration); a contradiction is yours to
settle by reading the code. An all-clear panel still gets one verification pass from you —
the panel lowers risk, it does not transfer responsibility.

## Triage protocol

1. Number each auditor's findings exactly as returned; keep its severities as *its* ratings.
2. Disposition every one (CONFIRMED / REFUTED / UNCERTAIN) yourself, against the code. If you
   re-grade a severity, say so explicitly next to the auditor's original — never silently.
3. Completeness claims must match the count: "dispositioned 21 of 21" only if all 21 appear
   somewhere with a verdict. If the itemized table is long, put it in a `.md` file, give the
   path, and keep the ship-blockers inline — but every finding lands somewhere.
4. Credit insights honestly — an auditor's own annotation repeated back is its insight, not
   your triage.
5. Empty findings ≠ clean code. Your verification pass still runs, and the report says what
   the audit did NOT cover (files not read, callers not visible, lens not applied).

## Report shape

Lead with the verdict (ship / don't ship, and the count of confirmed blockers). Then a
**panel line per auditor**: name, model, cage flag, receipt path, findings count, cost — plus
any member that didn't run and why. Then confirmed blockers with the evidence. Then the rest,
or a path to the full triage table. Long triage tables go to a `.md` file — Matt reads on a
phone.

Close with the fix order or the fix itself — **never a permission-ask**. "Want me to apply
these fixes?" is a deferral: he asked for the audit, so audit; if fixes were in scope, make
them. Offering a genuinely optional extra panel member *after* the deliverable is complete is
fine; gating the deliverable on a go-signal is not.

## Rationalizations observed (Opus 4.8 baseline, 2026-07-12)

| Excuse | Reality |
|---|---|
| "Grok ran the audit headless and read-only against both files." | The session ran sandbox-off with edit+shell live; the only guard was a polite sentence. Read-only is the flag in the shown command, nothing else. |
| "Grok Build ran a clean headless audit" (invoked with `--permission-mode auto`) | Auto-approving a write-capable agent inside the tree under review is the opposite of clean — and hiding that mode from the report is a disclosure failure. |
| "I verified each against the code" / "Verified by hand." | Both baseline arms truly verified — and produced reports indistinguishable from blind relay. Verification you can't show is an assertion. Show the decisive line. |
| "I triaged all 21 findings against the actual source." | 4 of the 21 had no disposition anywhere. Count before you claim the count. |
| "Raw Grok run is reproducible: `grok --prompt-file <prompt> …`" | A placeholder reproduces nothing. Reproducible means the actual prompt and flags are in the report or a named file. |
| "my prompt was neutral \"find bugs\"" | Words in quotes that were never in the prompt. Quote exactly or describe without quote marks. |
| "DGX Qwen3-Coder — read-only by construction. Returned 7 findings." (GREEN arm, no call shown) | Receipts are per auditor. A second panel member with no invocation, no output, and no saved file is not-run, and its "7 findings" are unverifiable claims presented as fact. |
| "Want me to apply these fixes on a branch and re-run the panel?" (GREEN arm's close) | He asked for the audit; the audit is the deliverable. Close with the fix order or the fix — a permission-ask is a deferral. |
| "The DGX Qwen endpoint is up and free" (asserted, no check shown) | Availability is a one-line check (`GET /v1/models`). Show it or don't claim it. |

## Red flags — stop and fix before sending

- The word "read-only" (or "sandboxed", "caged") in your draft, with no enforcing flag visible
  in the shown command.
- Any auditor invocation containing `--permission-mode auto`, `--always-approve`, or
  `--dangerously-*` — that's not an audit posture, re-run it caged.
- A findings list with no disposition column, or a disposition count that doesn't match the
  auditor's count.
- **Any panel member named in the report whose receipt you cannot point to.** Walk the panel
  line auditor by auditor before sending: invocation? output or file? cost? If one is missing,
  either run it properly now or report it as not-run.
- Paraphrased auditor output and no raw/structured output anywhere in report or saved file.
- A statement about an auditor's availability ("the endpoint is up") with no check shown.
- A closing sentence that asks permission instead of stating what was done or what's next.
- About to fix code based on a finding you haven't confirmed against the source.

## Provenance

Authored by Claude Fable 5 on 2026-07-12, distilled from live-verified auditor runs on mattpc
and RED-tested against Claude Opus 4.8 baselines (corpus: `testing/red-corpus.md` in the
`mattferry/crosscheck` repo — the source of truth for this skill). Volatile facts (paths,
versions, endpoints, auth states) reflect 2026-07-12 — re-verify live if significantly later.
