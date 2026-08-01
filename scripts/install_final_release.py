#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, io, tarfile
ROOT=Path(__file__).resolve().parents[1]
PARTS=ROOT/'scripts/final_release_payload'
EXPECTED='5144077895ecf550cc0b262915730f55f87d9bfa33b73b9e8679f79493babdd7'
parts=sorted(PARTS.glob('part-*.txt'))
if len(parts)!=10: raise SystemExit(f'expected 10 payload chunks, found {len(parts)}')
encoded=''.join(p.read_text(encoding='ascii').strip() for p in parts)
data=base64.b64decode(encoded,validate=True)
digest=hashlib.sha256(data).hexdigest()
if digest!=EXPECTED: raise SystemExit(f'payload checksum mismatch: {digest}')
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
    members=tar.getmembers()
    for member in members:
        target=(ROOT/member.name).resolve()
        if ROOT.resolve() not in target.parents and target!=ROOT.resolve(): raise SystemExit(f'unsafe path: {member.name}')
    tar.extractall(ROOT)
print(f'install_final_release: extracted {len(members)} files sha256={digest}')
