# Local / self-hosted OpenAI-compatible endpoints as auditors

The cheapest panel member: any OpenAI-compatible `/v1/chat/completions` endpoint. No agentic
tools, no filesystem access — you send it code, it sends back findings. **Structurally
read-only by construction**: the model never sees the tree, so it cannot touch it.

Works with SGLang, vLLM, LM Studio, Ollama, llama.cpp — they all expose the same shape. Put
your host, port, and model id in your `roster.md`; the pattern below is identical regardless.

## Availability check (always run it before claiming the member is up)

```bash
curl -sf --max-time 10 http://<HOST>:<PORT>/v1/models | jq -r '.data[].id'
```

PowerShell: `Invoke-RestMethod -Uri 'http://<HOST>:<PORT>/v1/models' -TimeoutSec 10 | % { $_.data.id }`

If it fails, the box is down or asleep — report the panel gap. Never narrate an audit from a
member you didn't reach.

## Canonical review call

Ask for a `file` key and tell the model which path it is reviewing — without it, findings from a
multi-file audit can't be attributed during triage, and the union-merge protocol needs
`file`+`line` identity.

```bash
jq -n --arg model '<MODEL_ID>' --arg path '<RELATIVE_PATH>' --rawfile code <FILE> '{
  model: $model, temperature: 0.2, max_tokens: 1200,
  messages: [
    {role: "system", content: "You are a strict code reviewer. Report every real defect as a JSON array of objects with keys: file, line, severity, summary. Set file to the path you were given. Output ONLY the JSON array."},
    {role: "user", content: ("Review this file (path: " + $path + "):\n\n" + $code)}
  ]}' | curl -sf --max-time 300 -X POST 'http://<HOST>:<PORT>/v1/chat/completions' \
        -H 'Content-Type: application/json' -d @- | tee audits/<name>-audit.json |
        jq -r '.choices[0].message.content'
```

PowerShell equivalent:

```powershell
$code = Get-Content <FILE> -Raw
$body = @{
  model = '<MODEL_ID>'; temperature = 0.2; max_tokens = 1200
  messages = @(
    @{ role = 'system'; content = 'You are a strict code reviewer. Report every real defect as a JSON array of objects with keys: file, line, severity, summary. Set file to the path you were given. Output ONLY the JSON array.' },
    @{ role = 'user'; content = "Review this file (path: <RELATIVE_PATH>):`n`n$code" }
  )
} | ConvertTo-Json -Depth 6
Invoke-RestMethod -Uri 'http://<HOST>:<PORT>/v1/chat/completions' -Method Post `
  -ContentType 'application/json' -Body $body -TimeoutSec 300 |
  ForEach-Object { $_.choices[0].message.content }
```

Save the raw response into your ignored receipts dir (`audits/` by convention) — that file is
this auditor's receipt. Redact hardcoded secrets before pasting: the endpoint (and anything
logging it) sees everything you send, and if the endpoint is unauthenticated, so does anyone
else who can reach it.

Parse defensively: a small local model follows "JSON only" most of the time, not always. Strip
fences and prose around the array before `ConvertFrom-Json`; on a parse failure, retry once with
"Output ONLY the JSON array, no prose." appended.

## Scope this auditor honestly

A chat endpoint sees **only what you paste**. It cannot explore the repo, chase imports, or read
callers — so per-file findings are reliable and whole-system findings are not. Feed it focused
units (one file, or a diff plus the context it touches), and say in the report that its view was
scoped. A large context window doesn't change this: quality drops when a small model is asked to
hold a whole subsystem at once.

Reference point: a 30B coder model reviews a ~35-line file in about 7 seconds and reliably
catches injection, silent-except, and comparison bugs — good value for a free panel seat.
