# Panel design — why external auditors, and how many

## The problem this solves

A model reviewing its own code shares every assumption that produced the bug. Self-review
catches typos; it structurally cannot catch "I misunderstood the requirement" or "my model
family systematically under-weights this failure mode." An auditor from a different model
family (xAI, OpenAI, a local Qwen) breaks the correlation — different training, different
blind spots, different priors about what "looks right."

This is the same argument as human code review, plus one AI-specific edge: model families
disagree *usefully*. When Grok and Qwen both flag a line Claude thought was fine, that
line is wrong more often than any single reviewer's hit rate predicts.

## Roles are fixed

- **Claude (the session) = author and orchestrator.** Applies fixes, owns the final report,
  owns verification of every finding.
- **External agents = auditors.** Read-only, structurally (sandbox/tool flags). They never
  edit the tree, never push, never merge. On the git side this is belt-and-suspenders with
  the `main-review-gate` ruleset (see memory `grok-under-claude-github`): even an agent with
  write credentials cannot reach `main` without a human-side approval.
- Findings flow one way: auditor → orchestrator → verification → report. An auditor's word
  is never quoted as a conclusion.

## Panel sizing

| Situation | Panel |
|---|---|
| Routine change, low blast radius | 1 auditor (cheapest available: local endpoint) |
| Ship-gate on real product code | 2 auditors from different families |
| Security-sensitive, money-adjacent, prod-touching | 2+ auditors, each explicitly prompted for a different lens (correctness / security / concurrency) |
| Auditor unavailable (auth, network) | Run the rest; REPORT the gap — a smaller panel is honest, a faked panel is not |

Diversity beats redundancy: two auditors with different lenses or families out-perform the
same auditor run twice. Don't ask the panel to vote — ask each for findings, then verify.

## Dissent handling

- **Agreement across families** (two auditors flag the same line): treat as near-confirmed;
  verify fast, fix.
- **Unique finding** (one auditor flags, others silent): normal — silence is not exoneration;
  verify it on the code like any other.
- **Direct contradiction** (one says defect, another says intended): the orchestrator reads
  the code and decides; record which auditor was right — over time this calibrates how much
  weight each panel member deserves.
- **All-clear from the whole panel**: still one verification pass by the orchestrator. The
  panel lowers risk; it does not transfer responsibility.

## Cost honesty

Grok bills Matt's grok.com subscription; Codex will bill a ChatGPT plan or API key; the DGX
endpoint is free. Reports name what was spent ("2 Grok calls, 1 local"). Quota exhaustion is
reported, not silently absorbed by shrinking the panel.
