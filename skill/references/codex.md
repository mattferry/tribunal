# OpenAI Codex CLI as a read-only QA auditor

CLI behavior verified against codex-cli 0.144.1 (2026-07-12), installed via
`npm install -g @openai/codex`. Record your machine's auth state in `roster.md`.

## Standing state

- Binary: `codex` (npm global).
- Auth options, in preference order:
  1. `codex login` — browser OAuth against a ChatGPT plan (needs a human at a screen, ~30s).
  2. `OPENAI_API_KEY` env var / `codex login --api-key` — needs an OpenAI API key.
- If neither is configured, Codex audits are UNAVAILABLE — say so in the report; never
  substitute a fabricated result. The other panel members still run.
- Check auth state cheaply: `codex login status`. **But auth ≠ availability**: a logged-in
  account can be quota-exhausted, and `login status` still says "Logged in" while every real
  call errors ("You've hit your usage limit … try again at <date>"). The only true availability
  check is a minimal real run; a quota error is a panel gap — report it with the error line as
  the receipt.
- **Confidentiality:** Codex (cloud) transmits what the auditor reads to OpenAI — same
  consideration as Grok; the `--oss` mode below keeps code local.

## Canonical audit invocation (once authed)

```bash
# Purpose-built review of the current repo — diffs ONLY (uncommitted changes + branch diff),
# not a full-tree audit:
codex exec review -C <REPO_DIR> --sandbox read-only

# General audit prompt with a schema-constrained verdict:
codex exec -C <DIR_TO_AUDIT> --sandbox read-only --skip-git-repo-check \
  --output-schema references/findings.schema.json \
  -o audits/codex-verdict.json \
  "Review <FILES> for real defects; report file, line, severity, summary."
```

(PowerShell: replace the `\` line continuations with backticks.)

- `--sandbox read-only` is **OS-level** enforcement (stronger than tool filtering) — model-run
  shell commands cannot write anywhere. This flag is NOT optional for auditing.
- `--output-schema <file>` constrains the final message to a JSON Schema (schema lives in a
  file, unlike Grok's inline flag) — a ready one ships at `references/findings.schema.json`.
  Note: OpenAI structured output requires `"additionalProperties": false` on **every** object;
  schemas without it are rejected (`invalid_json_schema`). `-o <file>` writes the final message
  to disk for parsing — route it into your ignored receipts dir (`audits/` by convention).
- `--json` streams JSONL events if progress visibility is needed.
- `--ephemeral` skips session persistence — good for fixture/scratch audits.

## Local-model escape hatch (no OpenAI auth needed)

`codex exec --oss --local-provider lmstudio ...` (or `ollama`) drives a locally served model
instead of OpenAI — same CLI, same sandbox. Useful to exercise the Codex harness before
committing to a ChatGPT plan; note the panel value of *OpenAI's models specifically* still
requires auth. Diversity caveat: if your roster already has a local endpoint serving the same
weights, `--oss` adds a harness, not a second model family — don't count it as one.

## Never

- Never `--dangerously-bypass-approvals-and-sandbox` for review work — its own help text says
  externally-sandboxed environments only, and an auditor never needs write access.
- Never let an unauthenticated Codex fail silently: report "Codex unavailable (no auth)" as a
  panel gap.
