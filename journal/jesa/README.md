# JESA preparation candidate

Source-owned review packet for **Journal of the Economic Science Association**, Original Paper. Status: **waiting-owner**. Approved public author/contact/support/relationship disclosures and source-reconstructed tool history are now implemented. Prior manager acceptance at `d73537e4a14e6fd378a2a25be52d51a73177f491` covers the scientific candidate. Manager acceptance of the author/disclosure update at `d36fc3dc0e8e17f7f6c0cf17f4eb008ef1bf3676` checked all 56 package and 1,078 baseline hashes, the scoped 29-file diff, disclosure/tool-history sources, and changed rendered pages (main 1/2/7, SI 2/3, instructions 2), retaining builder all-page bounds/visual QA. No content/layout defect was found within that bounded review. This is not independent specialist reproduction or author attestation. Final author and publisher gates remain; no submission, merge or public release occurred.

Start with `manuscript.pdf`, `supplement.pdf`, `data-instructions.pdf`, then `readiness.md`. Editable Markdown and TeX accompany each. `jesa-source.zip` contains portable article/supplement/instructions source plus vector figures. `package-manifest.json` pins this candidate; `evidence-manifest.json` pins every baseline tracked file at source main `62ab90beff1d291b069c87f13b6b6b3495171ddd`.

## Version map and corrections

| Identity | Meaning |
|---|---|
| journal/jesa/* | New JESA candidate; short main plus separate scientific and instruction appendices |
| docs/paper/paper.md and paper-draft.md | Byte-identical public manuscript at the baseline; preserved, not relabeled as journal source |
| arxiv/main.tex | Exact public-v1 TeX; preserved |
| arXiv2608.00979v1 | Posted August2,2026; distinct arXiv-processed PDF |
| arxiv-v1 tag f51f9374453e40480fb6290cbc35a0029dd6bd9a | Release identity, distinct from current code and artifact build-source88c64aa |
| docs/paper/PDF-README.md | Historical v14 pointer, superseded for this JESA package by this map |

The journal bibliography corrects Li Y/Ji X to **Zonghan Li/Feng Ji** and the intended v3 title; Persson E becomes **Joel Persson** at v3. Primary version links and all37 original entries appear in `reference-audit.json` (39 rows including2 additions). Xiao/Mousavi v1 metadata were valid for v1 and remain pinned. Horton is explicitly original2023; newer2026 authors are not silently assigned to the older version. No historical PDF, registration, public source, capsule, or release payload was edited. Public v2 is a separate owner decision.

Native `.github/workflows/arxiv-release.yml` automatically installs/seals/commits release surfaces on PRs touching `docs/paper/**` or root README. Keeping this candidate under `journal/jesa` avoids that workflow; do not move it to a watched path or run the release installer for journal preparation. No workflow, service, or automation was altered.

## Build and verification

Run `python3 journal/jesa/tools/build.py` from repository root. It uses installed Pandoc and Tectonic0.16.9, `--only-cached --untrusted`, no TeX installation or network dependency retrieval. The cache-minimal template uses standard core TeX packages and installed Times New Roman/Arial/Menlo fonts; font identities are in the build environment manifest. Exact PDF bytes may differ on another platform; compare extracted content and rendering, not a promise of cross-platform PDF-byte identity.

Run `python3 journal/jesa/tools/check_package.py` after building. Native `scripts/paper_submission_lint.py --base origin/main` remains required before commit. The public release build itself is not run because it mutates the frozen arXiv candidate and starts a server; this packet uses an isolated cached offline replay of the same native scientific audit logic.

The original `capsule/README.md` final line4,916 is an older confirmatory-only count, not the current full verifier denominator. Older hierarchy/review4,576 counts precede the completed Phase3 extension. This journal guide reconciles the boundary additively: **4,916 confirmatory +3 legacy =4,919 verifier runs;4,899 LLM runs +20 baselines**. Native receipts break down phases and calls. No silent update to historical instructions was made.

`author-metadata.json` contains only approved public author facts; the author authorized publication of the contact email and ORCID in this candidate. `declarations.md` and `tool-use-reconstruction.md/.json` record support, known relationships and recoverable AI roles. Raw intake, private answers, headshots and editorial correspondence remain outside public Git. `author-worksheet-template.md` contains public facts and remaining questions only.
