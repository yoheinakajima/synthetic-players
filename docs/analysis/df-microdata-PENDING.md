# DF2011 microdata reanalysis — PENDING external data

> **STATUS: FLAGGED STUB — R2 item 2, 2026-07-29. Nothing here is a
> result. Zero LLM calls.**

## What's missing

The Dal Bó & Fréchette (2011, AER 101(1):411–429) replication
microdata. The AEA/openICPSR package is **login-walled** from this
environment (HTTP 403 on `openicpsr.org`), and no officially mirrored
copy is reachable; per the honesty rules, no third-party mirror was
scraped and nothing was fabricated.

## Exact operator action needed

1. Log in at https://www.openicpsr.org (free account; institutional or
   ORCID login works) and open the AEA replication package for
   Dal Bó & Fréchette (2011), "The Evolution of Cooperation in
   Infinitely Repeated Games: Experimental Evidence" — reachable from
   the article page https://www.aeaweb.org/articles?id=10.1257/aer.101.1.411
   via its "Replication Package" link.
2. Download the package and drop the data files (`.dta` or `.csv`)
   into: **`data/external/df2011/`** (create the folder; it is
   gitignored by default — keep the raw files out of the repo unless
   the license permits redistribution).
3. Run:
   `cd artifacts/api-server && uv run --with pandas --with numpy python engine/r2_df_reanalysis.py`

## What is already done

- `engine/r2_df_reanalysis.py` is **fully written and selftested**
  against a synthetic fixture with the expected schema
  (`--selftest`; transcript output committed as
  `docs/analysis/r2/df2011-reanalysis-FIXTURE-SELFTEST.md`). Column
  aliases are handled; if the real schema differs, only `COLMAP` at the
  top of the script needs touching. The moment the data lands, the
  full analysis — first-exposure view, experienced/late views, learning
  trajectory, per-subject frequencies, endpoint mass, within/between
  variance, and the opportunity-count-downsampled panel — is one
  command.

## Scoped fallback (published-table values only)

Until the microdata lands, the only DF2011-derived quantities this
project may cite are the published-table pins already sealed in the
Phase 5 predicates (R=40 first-round cooperation 0.6110 / 0.1872;
between-subject SDs 0.3116 / 0.4122), now relabeled **published,
nonmatched comparator** everywhere (R2 relabeling pass; see
`docs/analysis/claim-dependencies.md`). No per-subject, endpoint-mass,
learning, or downsampled statement about DF2011 is permitted from
published tables alone — those claims stay out of the draft until this
stub is resolved.

## Design caveat that will survive the data landing

The DF2011 treatment was between-session: the human individual response
Δᵢ is unobserved in their design, so our within-persona Δᵢ has no
direct human analogue in this data regardless of what the microdata
shows. The reanalysis contextualizes; it cannot create a matched
comparison.
