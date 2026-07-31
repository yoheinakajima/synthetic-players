#!/usr/bin/env python3
"""Refresh the public capsule checksum manifest after the replay audit expansion.

The manifest is a deterministic list of ``sha256  ./relative/path`` entries.
Existing entries retain their order; newly required verifier files are appended
in sorted order. The manifest itself is intentionally not self-hashed.

Four replay reports are regenerated whenever ``capsule/verify.sh`` runs and
contain runtime-stamped fields. They are therefore verified by successful
recomputation, not treated as immutable capsule inputs. Hashing them in the
input manifest creates an unavoidable write-after-hash cycle, so they are
explicitly excluded below.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "capsule"
MANIFEST = CAPSULE / "SHA256SUMS.capsule"
REQUIRED_NEW = {
    "./verify.sh",
    "./artifacts/api-server/engine/phase3_replay_audit.py",
}
REGENERATED_OUTPUTS = {
    "./docs/phase4/step8-replay-audit.json",
    "./docs/phase4/step8-replay-audit.md",
    "./docs/phase5-close/replay-audit.json",
    "./docs/phase5-close/replay-audit.md",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    existing_order: list[str] = []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        _sha, rel = line.split(None, 1)
        rel = rel.strip()
        if rel in REGENERATED_OUTPUTS:
            continue
        if rel not in existing_order:
            existing_order.append(rel)

    for rel in sorted(REQUIRED_NEW):
        if rel not in existing_order:
            existing_order.append(rel)

    missing = [
        rel
        for rel in existing_order
        if not (CAPSULE / rel.removeprefix("./")).is_file()
    ]
    if missing:
        raise RuntimeError(f"capsule manifest references missing files: {missing}")

    lines = [
        f"{digest(CAPSULE / rel.removeprefix('./'))}  {rel}"
        for rel in existing_order
    ]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "update_capsule_manifest_v12: "
        f"{len(lines)} immutable inputs; "
        f"{len(REGENERATED_OUTPUTS)} replay-generated outputs excluded"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
