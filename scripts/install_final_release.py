#!/usr/bin/env python3
from pathlib import Path
import base64, hashlib, io, tarfile

ROOT = Path(__file__).resolve().parents[1]
PARTS = ROOT / 'scripts/final_release_chunks'
NAMES = [
    'part-00.txt', 'part-01.txt', 'part-02.txt', 'part-03.txt',
    'part-04-05.txt', 'part-06-07.txt', 'part-08-09.txt',
    'part-10-11.txt', 'part-12-13.txt', 'part-14-15.txt', 'part-16.txt',
]
EXPECTED = '4e86ae1d9ca2678888b2b7c4e6caffc057a0a8e4d6ef967b176305f4057e36f0'

missing = [name for name in NAMES if not (PARTS / name).is_file()]
if missing:
    raise SystemExit(f'missing payload chunks: {missing}')

encoded = ''.join((PARTS / name).read_text(encoding='ascii').strip() for name in NAMES)
try:
    data = base64.b64decode(encoded, validate=True)
except Exception as exc:
    raise SystemExit(f'payload base64 decode failed: {exc}')

digest = hashlib.sha256(data).hexdigest()
if digest != EXPECTED:
    raise SystemExit(f'payload checksum mismatch: {digest}')

with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as tar:
    members = tar.getmembers()
    root = ROOT.resolve()
    for member in members:
        target = (ROOT / member.name).resolve()
        if target != root and root not in target.parents:
            raise SystemExit(f'unsafe path: {member.name}')
    tar.extractall(ROOT)

print(f'install_final_release: extracted {len(members)} files sha256={digest}')
