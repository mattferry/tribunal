# tribunal

**Independent QA for AI-written code: a Claude Code skill + runbooks that put other coding
models on the review panel.**

The author of a change is the worst-placed agent to judge it. `tribunal` teaches a Claude Code
session to convene *external* coding agents — different model families, different blind spots —
as read-only auditors, then triage their findings with discipline instead of relaying them as
truth.

## What's here

```
skill/                   Copy this whole dir to ~/.claude/skills/tribunal/
  SKILL.md               The installable Claude Code skill
  roster.example.md      Template: your panel — copy to roster.md and fill in
  references/
    grok.md              Grok Build (xAI grok-4.5) as a read-only auditor — full runbook
    codex.md             OpenAI Codex CLI as a read-only auditor — full runbook
    local-openai.md      Any OpenAI-compatible endpoint (SGLang, vLLM, LM Studio, Ollama)
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

## Does it actually work?

Yes — and the test corpus is the interesting part.

**Without the skill** (2 Opus 4.8 arms, RED baseline): both did real work — ran Grok, read the
code, found all six seeded defects — and both produced reports that *proved nothing*. No
invocation shown, no auditor output shown. One ran Grok with the full default toolset (edit +
shell live) guarded only by the prompt sentence "do not modify any files", then told the user
it ran "read-only". The other used `--permission-mode auto` — auto-approving a write-capable
agent inside the directory it was judging — and called it "a clean headless audit".

**With the skill**: receipts per auditor, `--tools` allowlist enforced, every finding
dispositioned against the source. In one run Grok **hallucinated 6 of its 15 findings** — a
`cancel()` function that doesn't exist, line numbers 42–82 in a 26-line file — and the arm
caught all six, refuted them, and said so in the report. That is the thesis of this repo in one
data point: an external auditor is worth having *and* cannot be trusted unverified.

Full corpus: `testing/red-corpus.md`, `testing/green-results.md`.

## Status

Skill is RED/GREEN-tested and in use. Codex auditor is fully documented but awaits
authentication on this machine (`codex login`) — until then the panel runs Grok + local.
