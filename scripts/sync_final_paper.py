#!/usr/bin/env python3
"""Install the reviewed final manuscript exactly from small checked payload chunks."""
from pathlib import Path
import base64, hashlib, zlib
ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'docs/paper/paper.md'
ALIAS=ROOT/'docs/paper/paper-draft.md'
PAYLOAD_DIR=ROOT/'scripts/final_paper_payload'
EXPECTED_SHA256='8f7aaf1a7c3c5979a7fec724731f1ed0217a22fd2b1a8c12b79ec11a8a42ae7f'
EXPECTED_PARTS=4

def main():
    parts=sorted(PAYLOAD_DIR.glob('part-*.txt'))
    if len(parts)!=EXPECTED_PARTS:
        raise SystemExit(f'expected {EXPECTED_PARTS} payload parts, found {len(parts)}')
    encoded=''.join(p.read_text(encoding='ascii').strip() for p in parts)
    try:
        data=zlib.decompress(base64.b64decode(encoded,validate=True))
    except Exception as exc:
        raise SystemExit(f'final manuscript payload decode failed: {exc}')
    digest=hashlib.sha256(data).hexdigest()
    if digest!=EXPECTED_SHA256:
        raise SystemExit(f'final manuscript payload hash mismatch: {digest}')
    text=data.decode('utf-8')
    required=(
        '63%-71% under Jeffreys alpha=0.5 and 47%-53% under alpha=1',
        'The results concern one fixed model-prompt panel and do not establish human substitutability.',
        'A Phase 6 test will preregister the candidate family',
    )
    missing=[marker for marker in required if marker not in text]
    if missing:
        raise SystemExit(f'final manuscript markers missing: {missing}')
    PAPER.write_bytes(data)
    ALIAS.write_bytes(data)
    print(f'sync_final_paper: installed canonical manuscript sha256={digest} from {len(parts)} chunks')
if __name__=='__main__': main()
