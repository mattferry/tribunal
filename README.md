# crosscheck

**Independent QA for AI-written code: a Claude Code skill + runbooks that put other coding
models on the review panel.**

The author of a change is the worst-placed agent to judge it. `crosscheck` teaches a Claude Code
session to submit its own work to *external* coding agents — different model families, different
blind spots — as read-only auditors, then triage their findings with discipline instead of
relaying them as truth.

## What's here

```
skill/
  SKILL.md               The installable Claude Code skill (copy to ~/.claude/skills/crosscheck/)
  references/
    grok.md              Grok Build (xAI grok-4.5) as a read-only auditor — full runbook
    codex.md             OpenAI Codex CLI as a read-only auditor — full runbook
    local-openai.md      Any OpenAI-compatible endpoint (DGX SGLang, LM Studio) as an auditor
docs/
  panel-design.md        Why independent review, panel sizing, dissent handling
testing/
  briefs.md              RED/GREEN behavioral test methodology for this skill
  fixtures/              Seeded-defect fixture used by the tests
  red-corpus.md          Baseline failures observed WITHOUT the skill (what the skill must fix)
  green-results.md       Verification that the skill flips those failures
```

## The contract in one paragraph

An external audit is real only if all four hold: (1) the auditor actually ran — command and
output shown, never narrated; (2) the auditor was **structurally read-only** — sandbox/tool
flags, not politeness, prevent it from editing or running shell; (3) every finding was
**verified by the orchestrating agent against the code** before being acted on or reported —
findings are hypotheses, dissent between auditors is signal; (4) cost and availability are
reported honestly — an unauthenticated or unreachable auditor is reported as such, never
silently skipped or faked.

## Panel roster (as verified on mattpc, 2026-07-12)

| Auditor | Engine | Auth | Cost | Read-only enforcement |
|---|---|---|---|---|
| Grok Build (`grok.exe` 0.2.93) | grok-4.5 | grok.com OAuth (on disk) | Matt's xAI subscription | `--tools "read_file,grep,list_dir"` |
| Codex CLI (`codex` 0.144.1) | OpenAI (per plan) | **pending** `codex login` or `OPENAI_API_KEY` | ChatGPT plan / API | `--sandbox read-only` (OS-level) |
| DGX Qwen3-Coder-30B | local SGLang, tailnet | none | free | API-only — model never touches the tree |

## Status

Working skill, RED/GREEN-tested per the pack methodology (see `testing/`). Codex auditor is
fully documented but awaits authentication on this machine.
