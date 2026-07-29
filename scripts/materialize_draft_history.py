#!/usr/bin/env python3
"""Materialize exact historical manuscript files from temporary encoded parts.

The staging files were written through a text-only connector over several review
rounds. Some old transport chunks contain padding at intermediate boundaries.
This script tries a small, deterministic set of Base64 reconstruction strategies
and accepts a result only when the decoded manuscript matches the pinned SHA-256.
After successful materialization the staging directory is removed, leaving only
the reviewer-facing Markdown history.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import shutil
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
TEMP = ROOT / "docs" / "paper" / "history" / ".materialize"
MANIFEST = TEMP / "manifest.json"


def normalize(path: Path) -> str:
    return "".join(path.read_text(encoding="utf-8").split())


def padded(text: str) -> str:
    return text + ("=" * ((-len(text)) % 4))


def payload_candidates(texts: list[str]) -> Iterable[tuple[str, bytes]]:
    """Yield deterministic reconstruction candidates, deduplicated by bytes."""
    joined = "".join(texts)
    stripped_joined = "".join(t.rstrip("=") for t in texts)
    seen: set[bytes] = set()

    def emit(label: str, text: str, *, strict: bool) -> Iterable[tuple[str, bytes]]:
        try:
            value = base64.b64decode(padded(text), validate=strict)
        except Exception:
            return ()
        if value in seen:
            return ()
        seen.add(value)
        return ((label, value),)

    for item in emit("joined-strict", joined, strict=True):
        yield item
    for item in emit("joined-lenient", joined, strict=False):
        yield item
    for item in emit("padding-stripped-strict", stripped_joined, strict=True):
        yield item
    for item in emit("padding-stripped-lenient", stripped_joined, strict=False):
        yield item

    # Legacy possibility: each transport chunk was independently Base64 encoded.
    decoded_parts: list[bytes] = []
    for text in texts:
        try:
            decoded_parts.append(base64.b64decode(padded(text), validate=False))
        except Exception:
            decoded_parts = []
            break
    if decoded_parts:
        value = b"".join(decoded_parts)
        if value not in seen:
            yield "per-part-lenient", value


def decode_record(rec: dict, parts: list[Path]) -> tuple[bytes, str]:
    texts = [normalize(path) for path in parts]
    expected = rec["sha256"]
    compression = rec.get("compression")
    diagnostics: list[str] = []

    for label, payload in payload_candidates(texts):
        try:
            if compression is None:
                data = payload
            elif compression == "gzip":
                data = gzip.decompress(payload)
            else:
                raise RuntimeError(f"unsupported history compression: {compression}")
        except Exception as exc:
            diagnostics.append(f"{label}: decode ok, decompression failed ({exc})")
            continue
        digest = hashlib.sha256(data).hexdigest()
        if digest == expected:
            return data, label
        diagnostics.append(f"{label}: sha {digest}")

    names = ", ".join(str(path.relative_to(ROOT)) for path in parts)
    detail = "; ".join(diagnostics) or "no Base64 strategy decoded"
    raise RuntimeError(
        f"unable to materialize {rec['output']} from {names}; expected {expected}; {detail}"
    )


def main() -> int:
    if not MANIFEST.exists():
        print("materialize_draft_history: no manifest; nothing to do")
        return 0

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    outputs: list[str] = []
    for rec in manifest["drafts"]:
        parts = [TEMP / name for name in rec["parts"]]
        missing = [str(path.relative_to(ROOT)) for path in parts if not path.exists()]
        if missing:
            raise RuntimeError(f"missing draft-history parts: {missing}")
        data, strategy = decode_record(rec, parts)
        output = ROOT / rec["output"]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        outputs.append(f"{output.relative_to(ROOT)} ({strategy})")

    shutil.rmtree(TEMP)
    print("materialize_draft_history: wrote " + ", ".join(outputs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
