#!/usr/bin/env python3
"""Materialize exact historical manuscript files from temporary encoded parts.

Temporary part boundaries are transport-only and need not be valid Base64 on
their own. Concatenate normalized Base64 text, decode once, optionally
decompress the payload, verify the final manuscript SHA-256, write the exact
history files, and remove the temporary directory so only reviewer-facing
manuscripts remain.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMP = ROOT / "docs" / "paper" / "history" / ".materialize"
MANIFEST = TEMP / "manifest.json"


def main() -> int:
    if not MANIFEST.exists():
        print("materialize_draft_history: no manifest; nothing to do")
        return 0
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    outputs: list[str] = []
    for rec in manifest["drafts"]:
        parts = [TEMP / p for p in rec["parts"]]
        missing = [str(p.relative_to(ROOT)) for p in parts if not p.exists()]
        if missing:
            print(f"materialize_draft_history: waiting for parts: {missing}")
            return 0
        encoded = "".join(
            "".join(path.read_text(encoding="utf-8").split()) for path in parts
        )
        try:
            payload = base64.b64decode(encoded, validate=True)
        except Exception as exc:
            names = ", ".join(str(p.relative_to(ROOT)) for p in parts)
            raise RuntimeError(
                f"invalid concatenated Base64 history parts: {names}"
            ) from exc
        compression = rec.get("compression")
        if compression is None:
            data = payload
        elif compression == "gzip":
            data = gzip.decompress(payload)
        else:
            raise RuntimeError(f"unsupported history compression: {compression}")
        digest = hashlib.sha256(data).hexdigest()
        if digest != rec["sha256"]:
            raise RuntimeError(
                f"history SHA mismatch for {rec['output']}: {digest} != {rec['sha256']}"
            )
        output = ROOT / rec["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        outputs.append(str(output.relative_to(ROOT)))
    shutil.rmtree(TEMP)
    print("materialize_draft_history: wrote " + ", ".join(outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
