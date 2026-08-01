#!/usr/bin/env python3
"""Install the SHA-256-pinned canonical paper payload safely.

An already-verified provenance manifest is preserved across installation. The
payload contains a bootstrap manifest, but replacing a sealed manifest on every
verification run would create a non-convergent two-line provenance diff.
"""
from __future__ import annotations

import base64
import hashlib
import io
import json
import re
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "scripts/final_release_chunks"
PAYLOAD_SHA256 = "9b4789753b62f2f21ab7ea75cfeef462dfcbf7a62f704f070e129377ac74ad78"
PDF_SHA256 = "c5f153198eb7987d8fc2156902a412691d01188f38b5362c44f74c4f979c98f8"
SOURCE_SHA256 = "0b75e83583f58b2020feeee86ff999173a6d466be682a6b7471f950b36fdf0b1"
MARKDOWN_SHA256 = "b6c8a95d5eba541d23256b36ab3a1c64c4d89a4db52f66762291bc9409d00dc4"
MANIFEST = ROOT / "docs/paper/synthetic-players-artifact.json"


def preserved_manifest() -> bytes | None:
    if not MANIFEST.is_file():
        return None
    try:
        raw = MANIFEST.read_bytes()
        obj = json.loads(raw)
    except (OSError, json.JSONDecodeError, TypeError):
        return None

    required = {
        "repository": "yoheinakajima/synthetic-players",
        "source": "docs/paper/paper.md",
        "pdf": "docs/paper/synthetic-players.pdf",
        "pdf_sha256": PDF_SHA256,
        "arxiv_source": "docs/paper/synthetic-players-arxiv-source.zip",
        "arxiv_source_sha256": SOURCE_SHA256,
        "markdown_sha256": MARKDOWN_SHA256,
        "pages": 19,
        "figures": 5,
        "status": "verified release candidate",
    }
    if any(obj.get(key) != value for key, value in required.items()):
        return None
    if not re.fullmatch(r"[0-9a-f]{40}", str(obj.get("source_commit", ""))):
        return None
    if not re.fullmatch(
        r"https://github\.com/yoheinakajima/synthetic-players/actions/runs/[0-9]+",
        str(obj.get("workflow_run", "")),
    ):
        return None
    return raw


preserve = preserved_manifest()
raw = "".join(
    path.read_text(encoding="utf-8").strip()
    for path in sorted(CHUNKS.glob("payload-[0-9][0-9].txt"))
)
data = base64.b64decode(raw, validate=True)
actual = hashlib.sha256(data).hexdigest()
if actual != PAYLOAD_SHA256:
    raise SystemExit(f"final release payload hash mismatch: {actual}")

with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
    members = archive.getmembers()
    for member in members:
        target = (ROOT / member.name).resolve()
        if member.name.startswith("/") or target != ROOT.resolve() and ROOT.resolve() not in target.parents:
            raise SystemExit(f"unsafe release member path: {member.name}")
        if not member.isfile() or member.issym() or member.islnk() or member.isdev():
            raise SystemExit(f"unsafe release member type: {member.name}")
    archive.extractall(ROOT, members=members, filter="data")

if preserve is not None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_bytes(preserve)

print("installed final release", actual)
