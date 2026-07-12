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

## Supported auditors

Any coding agent that can be run headless and constrained to read-only. Out of the box:

| Auditor | Engine | Read-only enforcement |
|---|---|---|
| Grok Build (`grok`) | xAI grok-4.5 | `--tools "read_file,grep,list_dir"` (tool allowlist) |
| OpenAI Codex CLI (`codex`) | OpenAI models | `--sandbox read-only` (OS-level) |
| Any OpenAI-compatible endpoint | self-hosted / local (SGLang, vLLM, LM Studio, Ollama, llama.cpp) | API-only — the model never touches the tree |

You describe your own panel in `roster.md` (copied from `roster.example.md`) — which auditors
you have, how to invoke them, and what each costs. Full per-auditor runbooks in
`skill/references/`.

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

## Install

1. Copy `skill/` to `~/.claude/skills/tribunal/`.
2. Copy `roster.example.md` to `roster.md` in that directory and fill in the auditors you have.
3. Ask Claude Code for an external QA audit — the skill triggers on second-opinion / independent
   review requests.

## License

MIT — see [LICENSE](LICENSE).
