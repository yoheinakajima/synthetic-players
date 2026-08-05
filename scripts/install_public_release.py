#!/usr/bin/env python3
"""Install SHA-256-pinned final public release surfaces and derived site figures."""
# Final convergence trigger: validate the exact post-generation release tree.
from __future__ import annotations
import base64,hashlib,io,shutil,struct,subprocess,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CHUNKS=ROOT/'scripts/public_release_chunks'
PAYLOAD_SHA256='35201e31b7da0e4f3fdb1c9f5a3ffb5c7fa3fdb308ce209ab03eabfcacd154da'
EXPECTED={'ARXIV_SUBMISSION.md': 'b9161a7a8a8d380fa92ddcad822d9c9510384e310458b89162757ba412b31da9', 'CITATION.cff': 'a6fb3ba47b341e680ecf730b4fce99c1351263b70aa712292a09dfd71d275347', 'README.md': '48b46d1c5e1f005bb52f650656a5b10754fbd8d747e49ad87ff3ca7aac10b7fe', 'REVIEW.md': '038a5c84736881a1c0f63329157f6e9232d74cb8a9eadd8acc4f1502cdd8b8d4', 'docs/analysis/submission/p52-prior-sensitivity.csv': '6026845e686c5fee7185b18ca46ca71be867ca03c73456360970b0ec7cbbe3c2', 'docs/analysis/submission/p52-prior-sensitivity.json': '8751633e7cc4a6e9eb78e9e724d2e1d54e9dca1fee270b6367350d2c42a66007', 'docs/analysis/submission/p52-prior-sensitivity.md': 'c283a031aed26a0191a44a33ad74817459a7b5f93b69813a9a13ab5e0646076a', 'docs/paper/arxiv-metadata.txt': '4d764c7e8d147b16a6d7bba04cf88ccc48459151236122a0e804b36045e849e4', 'docs/reviews/round-14-middle-path-finalization.md': '304cece09d29f8cc26b7743b91ccf7f354e33f185506b7352ab0923e75d0263a'}
PARTS={
 'part-00.txt':('34b4345c13dda2cb1a71c2d375303009fe82d96e7d5a36c5da9141f00ecfa64d',2332),
 'part-01.txt':('6d8c2e475d70b54dbcb0a1cee30e28eff0ab6d07fc1a57f5791710636f9c4730',2332),
 'part-02.txt':('066a8aada1ae5d706bce541a260e71f3c54eb067cb0de7de5125b5475e572090',2332),
 'part-03.txt':('7a13136d6a98aae478d66870a491a06f3b38613a03f43036c9ad9b2e5c58af96',2332),
 'part-04.txt':('fdb6e90bb09aae9a0aa48b1fb74a456b1d6b9f0e92963b15e33d1a6ead51a42c',2332),
 'part-05.txt':('a6d4b2efd44e29ec4d80a9caee39081e82006350164ee893d064b4210a428c14',832),
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
if len(raw)!=12492: raise SystemExit(f'public release base64 length mismatch: {len(raw)}')
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
 # The project site graduated from the pinned one-page payload to a living,
 # generated surface (scripts/build_site.py + scripts/site_data.py); site/*
 # members were dropped from the payload with the arXiv:2608.00979 metadata
 # patch, and the historical P5-2 sentence patch that targeted the payload copy
 # is retired. The site/ guard below is defensive only. Canonical paper
 # artifacts remain pinned by scripts/install_final_release.py and the
 # workflow-level hash checks.
 for rel,want in EXPECTED.items():
  src=stage/rel
  if hashlib.sha256(src.read_bytes()).hexdigest()!=want: raise SystemExit(f'public release file hash mismatch: {rel}')
  if rel.startswith('site/'): continue
  dst=ROOT/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(src,dst)
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
