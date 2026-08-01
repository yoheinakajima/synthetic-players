#!/usr/bin/env python3
"""Install SHA-256-pinned final public release surfaces."""
from __future__ import annotations
import base64,hashlib,io,shutil,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHUNKS=ROOT/'scripts/public_release_chunks'
PAYLOAD_SHA256='1459f3cf44a2f69d48d946095de1f44ec2c26682a17485d67dc198a6c56107ae'
EXPECTED={'ARXIV_SUBMISSION.md': '027b33c057f9e682f76910bf8c7c470dc8f582a7798f422cf855702f34a9cadf', 'CITATION.cff': 'b3f94a135d45cbc55b249e1712c399581b7fc1644d3451c7e49709593170a831', 'README.md': '42dd5a22f46a90720aff74f0781de48ff9e66dc29a46e3084515e80cd8a1f82c', 'REVIEW.md': '038a5c84736881a1c0f63329157f6e9232d74cb8a9eadd8acc4f1502cdd8b8d4', 'docs/analysis/submission/p52-prior-sensitivity.csv': '6026845e686c5fee7185b18ca46ca71be867ca03c73456360970b0ec7cbbe3c2', 'docs/analysis/submission/p52-prior-sensitivity.json': '8751633e7cc4a6e9eb78e9e724d2e1d54e9dca1fee270b6367350d2c42a66007', 'docs/analysis/submission/p52-prior-sensitivity.md': 'c283a031aed26a0191a44a33ad74817459a7b5f93b69813a9a13ab5e0646076a', 'docs/paper/arxiv-metadata.txt': '583b1ce75b4e60609b7681037d99d116f90d3370476ab6e6c4f34e846cf0c44f', 'docs/reviews/round-14-middle-path-finalization.md': '304cece09d29f8cc26b7743b91ccf7f354e33f185506b7352ab0923e75d0263a', 'site/favicon.svg': '019b52bc3335448de1a06158acdd86d4ddee9830ffe15b9a647d6c15592fdcce', 'site/index.html': 'a4ec05d25dad608efcd03a25698f427739e2ca64b6ed95f904c91f12463b3336', 'site/robots.txt': '4baf119c5f08143dd9cd3135b36f03550d957d84b0ca2da6432f5aae9145abc4', 'site/script.js': 'b48d81d6c2f0c0c5ae3df7c489a2580ba2e5c321b0310e47af551276da143beb', 'site/sitemap.xml': '267e0931e1da363cf48dc7be42a0f3d65e9c2621ccd2291e4ae8c2c55db49735', 'site/styles.css': '63717a140501b5d4d47bc027f35ee2cde45dc9813439aa9cba637e42924e55d1'}
data=base64.b64decode(''.join(p.read_text().strip() for p in sorted(CHUNKS.glob('part-[0-9][0-9].txt'))),validate=True)
if hashlib.sha256(data).hexdigest()!=PAYLOAD_SHA256: raise SystemExit('public release payload hash mismatch')
with tempfile.TemporaryDirectory(prefix='synthetic-players-public-') as td:
 stage=Path(td)
 with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tf:
  members=tf.getmembers(); names=set()
  for m in members:
   p=Path(m.name)
   if not m.isfile() or m.issym() or m.islnk() or m.isdev() or m.name.startswith('/') or '..' in p.parts: raise SystemExit(f'unsafe member: {m.name}')
   names.add(m.name)
  if names!=set(EXPECTED): raise SystemExit('public release member set mismatch')
  tf.extractall(stage,filter='data')
 for rel,want in EXPECTED.items():
  src=stage/rel
  if hashlib.sha256(src.read_bytes()).hexdigest()!=want: raise SystemExit(f'public release file hash mismatch: {rel}')
  dst=ROOT/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
print('installed final public release',PAYLOAD_SHA256)
