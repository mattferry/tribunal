# Local / self-hosted OpenAI-compatible endpoints as auditors

The cheapest panel member: any OpenAI-compatible `/v1/chat/completions` endpoint. No agentic
tools, no filesystem access — you send it code, it sends back findings. Structurally read-only
by construction.

## DGX Spark Qwen3-Coder (verified 2026-07-12)

- Endpoint: `http://100.95.10.94:8000/v1` (tailnet; SGLang, boot-start service on the DGX).
- Model id: `qwen3-coder-30b-abl` (Qwen3-Coder-30B-A3B-Abliterated, BF16, 256K ctx, ~30 tok/s).
- Cost: free, private, no quota. Measured: single-file review in ~7s.
- Reachability check: `Invoke-RestMethod http://100.95.10.94:8000/v1/models` — if it fails, the
  DGX is down/asleep; report the gap, don't fake it.

### Canonical review call (PowerShell)

```powershell
$code = Get-Content <FILE> -Raw
$body = @{
  model = 'qwen3-coder-30b-abl'; temperature = 0.2; max_tokens = 1200
  messages = @(
    @{ role = 'system'; content = 'You are a strict code reviewer. Report every real defect as a JSON array of objects with keys: line, severity, summary. Output ONLY the JSON array.' },
    @{ role = 'user'; content = "Review this file:`n`n$code" }
  )
} | ConvertTo-Json -Depth 6
Invoke-RestMethod -Uri 'http://100.95.10.94:8000/v1/chat/completions' -Method Post `
  -ContentType 'application/json' -Body $body -TimeoutSec 300 |
  ForEach-Object { $_.choices[0].message.content }
```

Parse defensively: a 30B local model follows the JSON-only instruction most of the time, not
always. Strip fences/prose around the array before `ConvertFrom-Json`; on parse failure, retry
once with "Output ONLY the JSON array, no prose." appended.

## Scope honestly

- A chat endpoint sees ONLY what you paste. It cannot explore the repo, chase imports, or read
  callers — so per-file findings are reliable, whole-system findings are not. Feed it focused
  units (a file, a diff + touched context) and say in the report that its view was scoped.
- 256K context allows multi-file pastes; keep each call to one review unit anyway — quality
  drops when a small model is asked to hold a whole subsystem.

## Other endpoints

LM Studio on mattpc exposes the same API shape (`http://localhost:1234/v1` when its server is
running, model ids via `/v1/models`). Same pattern, same caveats. Any future vLLM/SGLang/llama.cpp
box on the tailnet slots in identically: verify `/v1/models`, then reuse the call above.
