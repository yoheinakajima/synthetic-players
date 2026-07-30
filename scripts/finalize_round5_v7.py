#!/usr/bin/env python3
"""Finalize Round 5 reviewer-facing generated artifacts.

Runs after the zero-call audit and manuscript integration. It corrects the
archive-manifest inventory, aligns generated sensitivity prose with the
finite-sample coverage rationale, records Round 5 completion status, and keeps
machine-readable and human-readable surfaces synchronized.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "analysis" / "submission" / "round5"
AUDIT_JSON = OUT / "round5-review-audit.json"
AUDIT_MD = OUT / "round5-review-audit.md"
SUMMARY = ROOT / "docs" / "analysis" / "submission" / "submission-analysis-summary.json"
EPISODE_MD = ROOT / "docs" / "analysis" / "submission" / "episode-cluster-sensitivity.md"
STATUS = ROOT / "docs" / "analysis" / "submission-blockers.md"
REVIEWS = ROOT / "docs" / "reviews" / "README.md"
CITATION = ROOT / "CITATION.cff"


def replace_if_present(text: str, old: str, new: str) -> str:
    return text.replace(old, new) if old in text else text


def manifest_record(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "path": str(path.relative_to(ROOT)),
        "mentionsEngineDb": "engine.db" in text,
        "lineCount": len(text.splitlines()),
    }


def update_audit() -> dict:
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    prov = audit["provenance"]
    manifests = {r["path"]: r for r in prov.get("archiveHashManifests", [])}
    for path in (
        ROOT / "capsule" / "SHA256SUMS.capsule",
        ROOT / "docs" / "phase4-close" / "SHA256SUMS.txt",
        ROOT / "docs" / "phase5-close" / "SHA256SUMS.txt",
    ):
        if path.exists():
            rec = manifest_record(path)
            manifests[rec["path"]] = rec
    prov["archiveHashManifests"] = [manifests[k] for k in sorted(manifests)]
    prov["engineSnapshotCoveredByManifest"] = any(r["mentionsEngineDb"] for r in manifests.values())
    audit["provenance"] = prov
    AUDIT_JSON.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary.setdefault("results", {}).setdefault("round5ReviewAudit", {})["provenance"] = prov
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    md = AUDIT_MD.read_text(encoding="utf-8")
    marker = "## A2 — completion provenance and tamper-evidence boundary"
    if marker not in md:
        raise RuntimeError("Round 5 audit Markdown missing A2 section")
    prefix = md.split(marker, 1)[0]
    request = prov.get("requestedCoverage", {}).get("phase4-5", {})
    response = prov.get("respondedCoverage", {}).get("phase4-5", {})
    section = f"""{marker}

For Phase 4–5, the event store contains complete rendered system and user text for **{request.get('systemPresent', 0):,}/{request.get('events', 0):,}** requests, bundle SHA-256 and deterministic request-body SHA-256 values, engine commit, provider route, and requested model. The live adapter independently hashed the deterministic fields it actually sent and aborted unless that value equaled the recorded mirror.

The corresponding response records contain raw completion text for **{response.get('rawTextPresent', 0):,}/{response.get('events', 0):,}** events and provider response IDs for **{response.get('responseId', 0):,}/{response.get('events', 0):,}** events. They do not contain a provider-signed response object or a separately chained receipt-time hash of the raw completion payload.

The released capsule’s `SHA256SUMS.capsule` includes `data/engine.db.xz`, and release/checksum artifacts have external timestamp proofs. That makes the published database snapshot tamper-evident relative to the released snapshot. Byte-exact replay proves reproducibility from that snapshot; neither mechanism independently proves that no alteration occurred between provider receipt and snapshot sealing.

Machine-readable audit: `round5-review-audit.json`. Field coverage: `figure-sources/provenance-field-coverage.csv`.
"""
    AUDIT_MD.write_text(prefix + section, encoding="utf-8")
    return audit


def update_episode_report() -> None:
    text = EPISODE_MD.read_text(encoding="utf-8")
    text = replace_if_present(
        text,
        "## Why the initially generated percentile bootstrap is not primary",
        "## Why the exact projection is the conservative reference sensitivity",
    )
    text = replace_if_present(
        text,
        "An ordinary nonparametric percentile bootstrap becomes degenerate when every sampled episode has the same outcome. It therefore does not quantify policy uncertainty at the exact corners and was rejected before integration into the paper. Its output is retained in the table as an audit trail, not used as the submission inference.",
        "The exact Clopper–Pearson projection supplies finite-sample coverage for the discrete episode mean and is therefore the conservative reference sensitivity. The percentile cluster bootstrap is retained because it was computed, but with six discrete episodes per arm it has no comparable finite-sample coverage guarantee and can understate uncertainty. Exact-corner degeneracy is not itself a false-positive mechanism for the strict interiority gate.",
    )
    text = text.replace("Percentile cluster bootstrap (discarded as primary)", "Percentile cluster bootstrap sensitivity")
    EPISODE_MD.write_text(text, encoding="utf-8")


def update_status(audit: dict) -> None:
    text = STATUS.read_text(encoding="utf-8")
    n6 = audit["exactGateAttainability"]["n6"]
    tail = audit["exactGateAttainability"]["currentFamilyTailAtMaxAttainableSlope"]
    text = text.replace("v6 paper", "v7 paper")
    text = text.replace("v6 Markdown manuscript", "v7 Markdown manuscript")
    text = text.replace("v6 reviewer bibliography/layout", "v7 reviewer bibliography/layout")
    text = replace_if_present(
        text,
        "The percentile cluster bootstrap is retained in the audit trail but rejected as the primary interval because it becomes degenerate when every observed episode agrees. Disagreement among the methods is reported as method sensitivity rather than resolved by selecting the favorable verdict.",
        "The exact Clopper–Pearson projection is the conservative finite-sample coverage reference. The percentile cluster bootstrap is retained as a post-adjudication sensitivity but has no comparable small-sample coverage guarantee at six discrete episodes per arm. Disagreement among the methods is reported as method sensitivity rather than resolved by selecting the favorable verdict.",
    )
    text = text.replace(
        "| Episode-cluster percentile bootstrap | p13, +0.4167 | 0.043455 | [0.042561, 0.044353] | Reported because computed; non-primary because percentile intervals degenerate at exact corners. |",
        "| Episode-cluster percentile bootstrap sensitivity | p13, +0.4167 | 0.043455 | [0.042561, 0.044353] | Reported because computed; no comparable finite-sample coverage guarantee at n=6. |",
    )
    text = text.replace(
        "| Conservative exact-episode CP (**primary sensitivity**) | p05/s2a, +0.0833 | 0.773206 | [0.771363, 0.775039] | p13 fails the episode-level interiority gate; only p04/s2p and p05/s2a survive. |",
        "| Conservative exact-episode CP sensitivity | p05/s2a, +0.0833 | 0.773206 | [0.771363, 0.775039] | p13 is gate-ineligible; at n=6 the family procedure is not powered for conventional rejection. |",
    )
    round5 = f"""
### A4. Explore Science Round 5 audits — **COMPLETE**

- the complete data-dependent gate is dynamically reapplied within every permutation; lookup/direct parity and a static-mask regression pass;
- at six episodes per arm, exact-gate-eligible means span only {n6['minPassingMean']:.3f}–{n6['maxPassingMean']:.3f}, the maximum eligible slope is {n6['maxAttainableSlope']:.3f}, and its archived-family null tail is {tail['pAddOne']:.6f};
- p13 is therefore neither prospectively confirmed nor decisively disconfirmed by an adequately powered conservative family procedure;
- completion provenance, receipt-time hashing limits, protocol definitions, representation confounds, and Figures 1/5 are corrected in v7.

Artifacts: `submission/round5/round5-review-audit.{{md,json}}` and `docs/reviews/round-5-disposition-matrix.md`.
"""
    if "### A4. Explore Science Round 5 audits" not in text:
        text = text.replace("## B. Human comparator", round5 + "\n## B. Human comparator")
    STATUS.write_text(text, encoding="utf-8")


def update_review_index() -> None:
    text = REVIEWS.read_text(encoding="utf-8")
    row = "| [`round-5-explore-science-review.md`](round-5-explore-science-review.md) / [`round-5-disposition-matrix.md`](round-5-disposition-matrix.md) | Explore Science review and response | Thirteen minor issues; dynamic-gate, power, provenance, construct, reporting, and figure corrections integrated into v7. |"
    if row not in text:
        table_end = "| [`round-4-independent-review.md`](round-4-independent-review.md) | Independent clone, lint, and full capsule reproduction on `main` at `8772a90` | Reproduced 4,576/4,576 runs, verified v5 numerically, and requested the final uncertainty, novelty, contrary-evidence, JSON, and PDF edits. |"
        text = text.replace(table_end, table_end + "\n" + row)
    REVIEWS.write_text(text, encoding="utf-8")


def update_citation() -> None:
    text = CITATION.read_text(encoding="utf-8")
    text = text.replace('version: "phase5-review-v6"', 'version: "phase5-review-v7"')
    CITATION.write_text(text, encoding="utf-8")


def main() -> int:
    audit = update_audit()
    update_episode_report()
    update_status(audit)
    update_review_index()
    update_citation()
    print("finalize_round5_v7: synchronized provenance, sensitivity rationale, status, and review index")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
