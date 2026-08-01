#!/usr/bin/env python3
"""Install SHA-256-pinned final public release surfaces and derived site figures."""
# Release convergence trigger: transactional capsule verification is now byte-clean.
from __future__ import annotations
import base64,hashlib,io,shutil,struct,subprocess,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHUNKS=ROOT/'scripts/public_release_chunks'
PAYLOAD_SHA256='1459f3cf44a2f69d48d946095de1f44ec2c26682a17485d67dc198a6c56107ae'
EXPECTED={'ARXIV_SUBMISSION.md': '027b33c057f9e682f76910bf8c7c470dc8f582a7798f422cf855702f34a9cadf', 'CITATION.cff': 'b3f94a135d45cbc55b249e1712c399581b7fc1644d3451c7e49709593170a831', 'README.md': '42dd5a22f46a90720aff74f0781de48ff9e66dc29a46e3084515e80cd8a1f82c', 'REVIEW.md': '038a5c84736881a1c0f63329157f6e9232d74cb8a9eadd8acc4f1502cdd8b8d4', 'docs/analysis/submission/p52-prior-sensitivity.csv': '6026845e686c5fee7185b18ca46ca71be867ca03c73456360970b0ec7cbbe3c2', 'docs/analysis/submission/p52-prior-sensitivity.json': '8751633e7cc4a6e9eb78e9e724d2e1d54e9dca1fee270b6367350d2c42a66007', 'docs/analysis/submission/p52-prior-sensitivity.md': 'c283a031aed26a0191a44a33ad74817459a7b5f93b69813a9a13ab5e0646076a', 'docs/paper/arxiv-metadata.txt': '583b1ce75b4e60609b7681037d99d116f90d3370476ab6e6c4f34e846cf0c44f', 'docs/reviews/round-14-middle-path-finalization.md': '304cece09d29f8cc26b7743b91ccf7f354e33f185506b7352ab0923e75d0263a', 'site/favicon.svg': '019b52bc3335448de1a06158acdd86d4ddee9830ffe15b9a647d6c15592fdcce', 'site/index.html': 'a4ec05d25dad608efcd03a25698f427739e2ca64b6ed95f904c91f12463b3336', 'site/robots.txt': '4baf119c5f08143dd9cd3135b36f03550d957d84b0ca2da6432f5aae9145abc4', 'site/script.js': 'b48d81d6c2f0c0c5ae3df7c489a2580ba2e5c321b0310e47af551276da143beb', 'site/sitemap.xml': '267e0931e1da363cf48dc7be42a0f3d65e9c2621ccd2291e4ae8c2c55db49735', 'site/styles.css': '63717a140501b5d4d47bc027f35ee2cde45dc9813439aa9cba637e42924e55d1'}
PARTS={
 'part-00.txt':('898e44359aa383bbe6c0b12f4dd74d4cb9c04c3e6231e24eb3e6e14885f9d433',2332),
 'part-01.txt':('fd13ca75a54bf3869d42e388362edf86140ebd955ae9d8c92f401f36df497dbf',2332),
 'part-02.txt':('6e44aacea1bff3d38369902445149e8362616004d0e449575ab03998ede0d7bd',2332),
 'part-03.txt':('c0bfddf4cbbde674528b9adb2a1d63fa2a4db100f7ecb870be2a13b717e0cf98',2332),
 'part-04.txt':('989c89a257da97b731390c3f2b977e8cc1f54abc49f876713a42ccf7d77c739d',2332),
 'part-05a.txt':('5b5f0e1980daca67e8227aa34b3fd52d5aba282e941d8a591347a69a1d9d3048',1166),
 'part-05b.txt':('e6723cf18cae06ab62eaad656e2913e39e995edee69a015552576e1fe37c30ca',1166),
 'part-06.txt':('4172ca06ae97aad0ad7895dc33e808415d630645b880b95ea88f092bc485ca54',2332),
 'part-07.txt':('e2222329e1c44a4aac6f056b12e0029b02d9ffb1d4789bf492802526115adffa',2316),
}
FIGURES={
 'between-prompt-share':('c352dea32a034758cd4aa8fa8581dcef3aaa61debf461c483641e05d74e8270b',(1409,769)),
 'prompt-indexed-delta':('1cf2a5533b021858921ce2acb2501eb4931bad1f4d3ae81250a2ce42f187376a',(1325,986)),
}
parts=[]
for name,(want,n) in PARTS.items():
 s=(CHUNKS/name).read_text().strip()
 got=hashlib.sha256(s.encode()).hexdigest()
 if len(s)!=n or got!=want: raise SystemExit(f'public release chunk mismatch: {name} chars={len(s)} sha256={got}')
 parts.append(s)
raw=''.join(parts)
if len(raw)!=18640: raise SystemExit(f'public release base64 length mismatch: {len(raw)}')
data=base64.b64decode(raw,validate=True)
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
site=ROOT/'site/index.html'
site_text=site.read_text(encoding='utf-8')
old='The historical P5-2 classification is preserved, but its Bayesian proximity to the 0.20 boundary is prior-dependent; the alpha=1 posterior crosses it.'
new='The historical P5-2 classification is preserved, but its Bayesian proximity to the 0.20 boundary is prior-dependent; the alpha=1 posterior median is 0.205 (95% interval [0.182, 0.231]) and crosses it.'
if site_text.count(old)!=1: raise SystemExit('public site P5-2 sentence mismatch')
site.write_text(site_text.replace(old,new),encoding='utf-8')
renderer=shutil.which('pdftoppm')
if not renderer: raise SystemExit('pdftoppm is required to build the site figure derivatives')
assets=ROOT/'site/assets'; assets.mkdir(parents=True,exist_ok=True)
for stem,(source_sha,dims) in FIGURES.items():
 source=ROOT/'arxiv/figures'/f'{stem}.pdf'
 if hashlib.sha256(source.read_bytes()).hexdigest()!=source_sha: raise SystemExit(f'canonical figure source hash mismatch: {source}')
 prefix=assets/stem
 subprocess.run([renderer,'-png','-singlefile','-r','180',str(source),str(prefix)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 output=prefix.with_suffix('.png'); header=output.read_bytes()[:24]
 if header[:8]!=b'\x89PNG\r\n\x1a\n' or len(header)<24: raise SystemExit(f'invalid PNG derivative: {output}')
 if struct.unpack('>II',header[16:24])!=dims: raise SystemExit(f'PNG derivative dimensions mismatch: {output}')
print('installed final public release',PAYLOAD_SHA256)
