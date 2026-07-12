# Grok Build as a read-only QA auditor

All facts live-verified 2026-07-12 on mattpc (grok 0.2.93). Full CLI docs: `~/.grok/README.md`.

## Standing state on mattpc

- Binary: `C:\Users\mferr\.grok\bin\grok.exe` (on PATH).
- Auth: OAuth to grok.com, persisted in `~/.grok/auth.json` — headless calls work from any
  child process with no login step. **Usage bills Matt's grok.com subscription.**
- If auth ever expires: `grok login` is browser-based — Matt's screen required. Report it as a
  blocker; do not fake the audit.
- Models: `grok-4.5` (default), `grok-composer-2.5-fast` (`grok models` to re-check).

## Canonical audit invocation

```powershell
grok --cwd <DIR_TO_AUDIT> `
  -p "<review prompt — say what to read and what to look for>" `
  --tools "read_file,grep,list_dir" `
  --max-turns 12 `
  --json-schema '{"type":"object","properties":{"findings":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string"},"summary":{"type":"string"}},"required":["file","line","severity","summary"]}}},"required":["findings"]}'
```

- Output is a JSON object; parse the `structuredOutput` field — it is schema-validated, no
  regex scraping. `text`, `sessionId`, `stopReason` also present.
- `--tools "read_file,grep,list_dir"` is the read-only guarantee: the allowlist strips
  `search_replace` (edit), `run_terminal_cmd` (shell), and web tools from the toolset
  entirely. This flag is NOT optional for auditing.
- `--cwd` scopes what the auditor sees. Point it at the code under review, not at `~`.

## Useful variants

| Need | Flag |
|---|---|
| Review a diff, not a tree | Pipe/inline the diff into `-p`; keep the tools allowlist so it can read context |
| Multi-call conversation with the auditor | `-s <uuid>` on first call, `--resume <uuid>` after |
| Second opinion with self-verification | `--check` (appends a self-verify loop; headless only) |
| N independent attempts, best picked | `--best-of-n <N>` (headless only) |
| Deterministic-ish fast pass | `-m grok-composer-2.5-fast --effort low` |
| Streaming progress | `--output-format streaming-json` |

## Never

- Never run an audit with default tools or `--always-approve` — default Grok has edit + shell.
- Never use `--permission-mode bypassPermissions`/`auto` for review work.
- Never treat an empty `findings` array as "code is clean" — it is one model's opinion, and the
  orchestrator still owes its own verification pass.
