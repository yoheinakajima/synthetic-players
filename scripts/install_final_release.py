#!/usr/bin/env python3
from pathlib import Path
import base64,hashlib,io,tarfile
R=Path(__file__).resolve().parents[1]; P=R/'scripts/final_release_chunks'; raw=''.join(p.read_text().strip() for p in sorted(P.glob('payload-[0-9][0-9].txt'))); data=base64.b64decode(raw,validate=True); assert hashlib.sha256(data).hexdigest()=='9b4789753b62f2f21ab7ea75cfeef462dfcbf7a62f704f070e129377ac74ad78'
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:
 for m in t.getmembers(): q=(R/m.name).resolve(); assert q==R.resolve() or R.resolve() in q.parents
 t.extractall(R)
print('installed final release',hashlib.sha256(data).hexdigest())
