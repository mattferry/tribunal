# Grok Build as a read-only QA auditor

CLI behavior verified against grok 0.2.93 (2026-07-12). Full CLI docs ship at `~/.grok/README.md`
once installed. Put your machine's concrete values (binary path, auth state, which models are
enabled) in `roster.md`.

## Standing state

- Binary: `grok` (the installed CLI, on PATH). Install:
  `curl -fsSL https://x.ai/cli/install.sh | bash` (update later with `grok update`).
- Auth: OAuth to grok.com, persisted in `~/.grok/auth.json` — once logged in, headless calls
  work from any child process with no login step. **Usage bills your grok.com subscription.**
- If auth expires: `grok login` is browser-based and needs a human at a screen. Report it as a
  blocker; do not fake the audit.
- Models: `grok-4.5` (default), `grok-composer-2.5-fast` (`grok models` to list what's enabled).
- **Confidentiality:** Grok is a cloud service — every file the auditor reads is transmitted to
  xAI. Keep code you can't share externally off this auditor (use a local endpoint instead), and
  point it at a clean checkout: `.env` files or keys inside the scoped dir will be read and sent
  like any other file.

## Canonical audit invocation

```bash
grok --cwd <DIR_TO_AUDIT> \
  -p "<review prompt — say what to read and what to look for>" \
  --tools "read_file,grep,list_dir" \
  --max-turns 12 \
  --json-schema '{"type":"object","properties":{"findings":{"type":"array","items":{"type":"object","properties":{"file":{"type":"string"},"line":{"type":"integer"},"severity":{"type":"string"},"summary":{"type":"string"}},"required":["file","line","severity","summary"]}}},"required":["findings"]}'
```

(PowerShell: replace the `\` line continuations with backticks.)

- Output is a JSON object; parse the `structuredOutput` field — it is schema-validated, no
  regex scraping. `text`, `sessionId`, `stopReason` also present. Save the raw output under
  your ignored receipts dir (`audits/` by convention) — it is this auditor's receipt.
- `--tools "read_file,grep,list_dir"` is the read-only guarantee, and it works by **allowlist
  semantics: only the three named tools exist in the session** — edit, shell, and web tools
  (whatever the current version names them) are simply absent. This flag is NOT optional for
  auditing.
- `--cwd` scopes what the auditor sees. Point it at the code under review, not at `~` — and
  remember scoping is not confidentiality (see Standing state).

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
