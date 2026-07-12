# OpenAI Codex CLI as a read-only QA auditor

Facts verified 2026-07-12 on mattpc (codex-cli 0.144.1, installed globally via
`npm install -g @openai/codex`).

## Standing state on mattpc

- Binary: `codex` (npm global, Node 24).
- **Auth: NOT configured as of 2026-07-12.** Options, in preference order:
  1. `codex login` — browser OAuth against a ChatGPT plan (Matt's screen, ~30s).
  2. `OPENAI_API_KEY` env var / `codex login --api-key` — needs an OpenAI API key
     (none in the vault as of 2026-07-12).
- Until one of those happens, Codex audits are UNAVAILABLE — say so in the report; never
  substitute a fabricated result. The other panel members still run.
- Check auth state cheaply: `codex login status`.

## Canonical audit invocation (once authed)

```powershell
# Purpose-built review of the current repo (uncommitted changes + branch diff):
codex exec review -C <REPO_DIR> --sandbox read-only

# General audit prompt with a schema-constrained verdict:
codex exec -C <DIR_TO_AUDIT> --sandbox read-only --skip-git-repo-check `
  --output-schema findings.schema.json `
  -o codex-verdict.json `
  "Review payments.py and orders.py for real defects; report file, line, severity, summary."
```

- `--sandbox read-only` is **OS-level** enforcement (stronger than tool filtering) — model-run
  shell commands cannot write anywhere. This flag is NOT optional for auditing.
- `--output-schema <file>` constrains the final message to a JSON Schema (schema lives in a
  file, unlike Grok's inline flag). `-o <file>` writes the final message to disk for parsing.
- `--json` streams JSONL events if progress visibility is needed.
- `--ephemeral` skips session persistence — good for fixture/scratch audits.

## Local-model escape hatch (no OpenAI auth needed)

`codex exec --oss --local-provider lmstudio ...` drives a model served by LM Studio (installed
on mattpc) instead of OpenAI — same CLI, same sandbox. Useful if Matt wants the Codex harness
before deciding on a ChatGPT plan; the panel value of *OpenAI's models* still requires auth.

## Never

- Never `--dangerously-bypass-approvals-and-sandbox` for review work — its own help text says
  externally-sandboxed environments only, and an auditor never needs write access.
- Never let an unauthenticated Codex fail silently: report "Codex unavailable (no auth)" as a
  panel gap.
