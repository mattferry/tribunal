# Cursor CLI (`cursor-agent`) as a read-only QA auditor

A second LLM family for the panel **without OpenAI**: Cursor's own model, `composer-2.5`, is
distinct from Claude and from Grok, so it decorrelates from both the orchestrator and a direct
Grok seat. CLI behavior verified against `cursor-agent 2026.07.09` (2026-07-14). Record your
machine's auth state and model choice in `roster.md`.

## Standing state

- Binary: `cursor-agent` (on Windows a `.ps1` shim under `%LOCALAPPDATA%\cursor-agent\`; run it
  from PowerShell). `cursor-agent login` authenticates against a Cursor subscription (browser).
- Models: `cursor-agent --list-models`. **Pick `composer-2.5`** — it is Cursor's in-house model,
  a genuinely different family. Do NOT pick a `claude-*`/`fable-*` model (it correlates with the
  Claude orchestrator) or `cursor-grok-*` (that just duplicates a direct Grok seat) — either
  defeats the whole point. `gpt-5.*` models exist here too; they bill Cursor, not OpenAI directly,
  but `composer-2.5` avoids OpenAI's model entirely.
- **Confidentiality:** Cursor is a cloud service — every file the auditor reads is transmitted to
  Cursor's backend. Keep code you can't share externally off this seat; point it at a clean
  checkout, not a working dir with secrets.

## Canonical audit invocation

```bash
cursor-agent --print --output-format json --mode plan --trust \
  --model composer-2.5 --workspace <DIR_TO_AUDIT> \
  'Review the files for real defects (injection, money-handling, races, error handling). Respond with ONLY {"findings":[{"file","line","severity","summary"}]}, no prose.'
```

- `--mode plan` is the read-only cage: it is "read-only/planning — analyze, propose plans, no
  edits". **Verified 2026-07-14** — asked to write a file and run a shell command in plan mode, the
  agent refused and nothing landed on disk. This flag is NOT optional. Belt-and-suspenders:
  add `--sandbox enabled`.
- `--print` is headless (script) mode; **on its own it has write + shell access** (`--help` says
  so) — never run `--print` for an audit without `--mode plan`. `-f`/`--force`/`--yolo` are the
  opposite of a cage; never use them for review.
- `--output-format json` wraps the run as `{"type":"result","result":"<the model's text>"}`.
  Parse the top-level `.result`, then extract the `{"findings":[...]}` block from inside it (there
  may be a sentence of preamble before the JSON — unlike Grok, `cursor-agent` has no
  `--json-schema`, so validate the JSON you extract and re-prompt if it isn't clean). Save the raw
  output under your ignored receipts dir (`audits/`) — it is this auditor's receipt.
- Fast: a two-file review returns in ~30s (quicker than Grok's agentic sweep).

## Never

- Never `--print` without `--mode plan` (or `--sandbox enabled`) — headless print mode is
  write- and shell-capable by default.
- Never `-f`/`--force`/`--yolo`/`--auto-review` for an audit — those approve tool calls, the
  opposite of a read-only cage.
- Never pick a Claude/Fable model as the "external" auditor — same family as the orchestrator is
  not an independent opinion.
