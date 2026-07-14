# Example report — the shape the skill requires

A condensed, genericized version of a real passing run (single-auditor scenario, g1). Use the
shape, not the words: verdict first, a panel line per member, dispositions with evidence,
costs/gaps, a fix-order close. Placeholders in `<angle brackets>`.

---

**Verdict: DO NOT SHIP — 3 confirmed blockers** (SQL injection, negative-amount charge,
swallowed refund failures). 14 auditor findings triaged: 11 CONFIRMED, 2 REFUTED, 1 duplicate.

## Panel

| Auditor | Model | Cage | Receipt | Findings | Cost |
|---|---|---|---|---|---|
| Grok Build | grok-4.5 | `--tools "read_file,grep,list_dir"` | `audits/grok-audit.json` | 14 | 1 call (xAI subscription) |
| Codex CLI | — | — | `audits/codex-check.txt` | **did not run** — `codex login status`: not logged in | 0 |

Prompt sent to Grok (verbatim): "Review payments.py and orders.py for real defects: injection,
data integrity, concurrency, error handling. Report file, line, severity, summary."

## Confirmed blockers (evidence shown)

1. **SQL injection — `payments.py:8-9` (Grok #1, CONFIRMED).** `user_id` is f-string-interpolated
   into the SELECT: `f"SELECT balance FROM wallets WHERE user_id = '{user_id}'"`. Same pattern in
   the UPDATE at lines 16-19.
2. **Negative-amount charge mints money — `payments.py:15` (Grok #4, CONFIRMED — reproduced).**
   `charge(db, 'u1', -50.0)` returns `True` and the balance goes `100 → 150`. Three-line repro in
   `audits/repro.txt`.
3. **Refund failures vanish — `payments.py:33-34` (Grok #7, CONFIRMED).** `except Exception:
   pass` — a failed refund UPDATE reports success to the caller.

## Rest of the triage

Full table: `audits/grok-triage.md` (14 rows, one disposition each). Notables: Grok #11 REFUTED —
it claimed the refund UPDATE is injectable, but lines 28-31 use `?` placeholders (parameterized);
Grok #13 is a duplicate of #8 (same TOCTOU window, dup noted, not dropped). One severity
re-graded: #9 MEDIUM → LOW (auditor's original rating kept alongside).

Not covered by this audit: no caller of `reserve()` was in scope, so misuse patterns upstream
were not assessed; Codex seat empty (gap above).

## Fix order

1. Parameterize both queries in `charge()` (blocker 1).
2. Reject `amount <= 0` in `charge()` and `qty <= 0` in `reserve()` (blocker 2).
3. Replace `except Exception: pass` with logged failure + `False` return (blocker 3).
4. Then the four MEDIUMs in the triage table, in listed order.

(The ask was report-only, so this fix order is the close — the tree is untouched. Note the
close states what's next; it does not ask permission.)
