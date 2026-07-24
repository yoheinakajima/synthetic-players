# X1 Semantic-Equivalence Evidence — audit instrument and status

Sign-off §2.2 deliverable. Two components: (1) a structured **human** audit (primary
evidence), (2) model-based ratings (**supplementary only, never proof**). Status of each is
tracked here; neither has run yet. Model-rating calls are LLM calls and are therefore
**blocked until the one-line approval** (they are counted in the budget packet under
"semantic-rating calls").

## 1. Structured human audit instrument (primary)

Design: **two blinded readers**, independent completion, disagreements disclosed verbatim —
never reconciled silently. Readers see the three bundles labeled A/B/C in randomized order
without being told which is v1/v2a/v2b or what any arm's results were.

Each reader answers, per bundle pair (A↔B, A↔C, B↔C), strictly from the text:

| # | Checklist item | Answer set |
|---|---|---|
| 1 | Do both prompts describe the same two-player simultaneous binary-choice game? | same / different / unclear |
| 2 | Are the four payoff outcomes numerically identical and attached to the same action pairs? | same / different / unclear |
| 3 | Is the continuation process identical (same probability, same "after each round" semantics)? | same / different / unclear |
| 4 | Is the information available to the chooser identical (own/other past actions, both payoffs)? | same / different / unclear |
| 5 | Is the required response format identical (single token from {J, F})? | same / different / unclear |
| 6 | Does either prompt contain any additional incentive-relevant content the other lacks (norms, social cues, framing, urgency)? | none / list verbatim |
| 7 | Free field: any span you judge *not* meaning-preserving, quoted verbatim. | text |

Scoring rule (frozen): the pair is *audit-equivalent* iff both readers answer "same" on
items 1–5 and "none" on item 6. Any other pattern is published as-is in the report with
both readers' verbatim answers.

**Status: PENDING — requires two human readers.** The instrument above is frozen; reader
recruitment is outside the agent's control and is flagged in the freeze packet as an open
item that does not block Phase 4 runs (it amends the X1 *report*, not the X1 evidence).

## 2. Model-based ratings (supplementary only)

Protocol (frozen; runs only after approval):

- Raters: 3 models — `gpt-4.1` (the subject configuration itself is *excluded* as a rater;
  use distinct rater deployments), `claude-haiku-4-5`, and one additional model fixed at
  approval. Exact returned model identifiers archived per rating call.
- Each rater receives each ordered bundle pair once per direction (v1↔v2a, v1↔v2b,
  v2a↔v2b; both directions) at temperature 0, and completes the same 7-item checklist as
  the human instrument, answering in a fixed JSON schema.
- Exact rating prompt (verbatim, single user message; `{X}` and `{Y}` are the two complete
  serialized bundles including system, user, history block, and retry suffix):

> You will compare two instruction texts for a decision-making study. Do not evaluate which is better written. Judge only whether they specify the same decision problem. Text 1: {X} ——— Text 2: {Y} ——— Answer in JSON with keys q1..q6 (values "same", "different", "unclear", or for q6 "none" or a quoted list) and q7 (string, possibly empty), matching this rubric: [items 1–7 verbatim as in the human instrument].

- Raw JSON ratings are archived and published unmodified; a rating call that fails schema
  validation is republished raw and excluded from tallies (count disclosed).
- Budget: 3 raters × 3 pairs × 2 directions = **18 calls**, one attempt each, no retries.

**Status: PENDING APPROVAL (18 rating calls in budget packet).**

## 3. What this evidence can and cannot establish

The audit tests whether v1/v2a/v2b *specify the same game to a careful reader*. It cannot
establish that they are equivalent *stimuli for the subject model* — X1's result is
precisely that they are not. Equivalence-of-specification plus divergence-of-behavior is
the finding; this document exists to secure the first conjunct against the objection that
the rewordings smuggled in incentive-relevant content.
