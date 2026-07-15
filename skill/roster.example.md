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
| Cursor CLI | `cursor-agent --print --output-format json --mode plan --trust --model composer-2.5 --workspace <DIR> "<prompt>"` | `cursor-agent login` — Cursor subscription | `--mode plan` (read-only/planning — no edits, no shell) | Yes — Cursor cloud | `cursor-agent --list-models` (auth) |
| Deterministic scanner | `bandit -r <DIR> -f sarif -o audits/bandit.sarif` · `ruff check <DIR> --select S,B --output-format sarif` | none — free, local | read-only by construction (only reads files) | No — runs locally | `bandit --version` / `ruff --version` (a local binary) |

## Notes on filling it in

- **Cost column matters.** The skill requires reporting what each audit spent. "Free/local" is
  a legitimate entry; blank is not.
- **A local OpenAI-compatible endpoint is the cheapest panel member** — SGLang, vLLM, LM Studio,
  Ollama, llama.cpp all expose the same `/v1` shape. Any coding model works; a 30B coder is
  plenty for per-file review.
- **An auditor with no read-only enforcement doesn't belong on the roster.** If a CLI can't be
  caged with a flag, either don't use it for audits or run it against a copy of the tree it
  can't harm.
- **Keep at least one deterministic scanner on the roster.** It is free, local (no egress), and
  never hallucinates — the one seat that decorrelates an otherwise all-LLM panel. `bandit`/`ruff`
  install with `pip` and run natively; `semgrep` is multi-language (Linux/macOS/WSL/Docker). Full
  runbook: `references/static-analysis.md`.
- Adding an auditor = one row here + a runbook in `references/` (next to this file).
