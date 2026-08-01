#!/usr/bin/env python3
from pathlib import Path
import hashlib, tarfile
ROOT=Path(__file__).resolve().parents[1]
PAYLOAD=ROOT/'scripts/final_release_payload.tar.gz'
EXPECTED='70d69abf55f0038a94f378387d1c586606a395b3453c371dda54009dba477677'
data=PAYLOAD.read_bytes()
digest=hashlib.sha256(data).hexdigest()
if digest!=EXPECTED:
    raise SystemExit(f'payload checksum mismatch: {digest}')
with tarfile.open(PAYLOAD,'r:gz') as tar:
    members=tar.getmembers()
    for member in members:
        target=(ROOT/member.name).resolve()
        if ROOT.resolve() not in target.parents and target!=ROOT.resolve():
            raise SystemExit(f'unsafe path: {member.name}')
    tar.extractall(ROOT)
print(f'install_final_release: extracted {len(members)} files sha256={digest}')
