---
name: Metric presentation traps
description: Presentation and metric-validity rules learned from mislabeled game-theory stats
---

# Metric presentation traps

**Rules.**
1. Never surface cumulative totals where per-round/normalized values are
   expected — compute and store per-unit averages server-side, lead with them,
   and label totals explicitly as totals.
2. Never report a metric for a domain class where it is undefined. Represent
   it as null/absent, not 0 — a 0 reads as a finding. Make display panels
   class-aware.
3. When a rate has strict and loose variants (e.g. mutual vs action-level
   cooperation), name both explicitly; an unlabeled "rate" invites silent
   redefinition.

**Why:** the lab UI showed "1.0 / 4.0" payoffs (correct 50-round totals) in a
context that read as per-round nonsense; "cooperation rate" was reported for
zero-sum games where cooperation doesn't exist; a per-round "Nash equilibrium
rate" was shown for mixed-equilibrium games where it reads 0% for optimal play.
All were correct numbers presented as wrong claims.

**How to apply:** when adding any aggregate stat to an API/UI/report, decide
per-unit vs total at the schema level, gate each metric on domain class
validity (null elsewhere), and give strict/loose variants distinct names.
