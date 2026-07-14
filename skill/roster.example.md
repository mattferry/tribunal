# Panel roster — fill this in for your machine

The skill reads your roster to know which auditors exist, how to invoke them, how they're
caged, and what they cost. Copy this to `roster.md` in the same directory (gitignored in the
tribunal repo so a machine-specific roster never gets committed; after install it's just a
local file) and replace the placeholders with your real values.

**Verify every line live before trusting it** — auth states and endpoints go stale. The skill's
whole premise is receipts.

## Template

| Auditor | Invoke | Auth / cost | Read-only enforcement | Code leaves machine? | Verify it's up |
|---|---|---|---|---|---|
| Grok Build | `grok --cwd <DIR> -p "<prompt>" --tools "read_file,grep,list_dir"` | grok.com OAuth (`~/.grok/auth.json`) — bills your xAI subscription | `--tools` allowlist (no edit/shell in the set) | Yes — xAI cloud | `grok models` (auth) — quota still needs a real call |
| Codex CLI | `codex exec -C <DIR> --sandbox read-only "<prompt>"` | `codex login` (ChatGPT plan) or `OPENAI_API_KEY` | `--sandbox read-only` (OS-level) | Yes — OpenAI cloud | `codex login status` (auth ONLY — a quota-blocked account still says "Logged in"; the true check is a minimal real call) |
| Local model | `POST http://<HOST>:<PORT>/v1/chat/completions` | none (self-hosted) | API-only — never sees the tree | No | `GET /v1/models` |

## Notes on filling it in

- **Cost column matters.** The skill requires reporting what each audit spent. "Free/local" is
  a legitimate entry; blank is not.
- **A local OpenAI-compatible endpoint is the cheapest panel member** — SGLang, vLLM, LM Studio,
  Ollama, llama.cpp all expose the same `/v1` shape. Any coding model works; a 30B coder is
  plenty for per-file review.
- **An auditor with no read-only enforcement doesn't belong on the roster.** If a CLI can't be
  caged with a flag, either don't use it for audits or run it against a copy of the tree it
  can't harm.
- Adding an auditor = one row here + a runbook in `references/` (next to this file).
