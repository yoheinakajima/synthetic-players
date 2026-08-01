#!/usr/bin/env python3
from pathlib import Path
import base64,gzip,hashlib,io,json,shutil,tarfile
R=Path.cwd(); W=Path('/tmp/final-release'); S=Path('/tmp/release-stage'); shutil.rmtree(S,ignore_errors=True)
for p in ['arxiv/main.tex','arxiv/figures/between-prompt-share.pdf','arxiv/figures/condition-means.pdf','arxiv/figures/p13-audit.pdf','arxiv/figures/prompt-indexed-delta.pdf','arxiv/figures/representation-effects.pdf']:
 q=S/p; q.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(W/p,q)
for n in ['paper.md','paper-draft.md']:
 q=S/'docs/paper'/n; q.parent.mkdir(parents=True,exist_ok=True); q.write_bytes((W/'paper.md').read_bytes())
shutil.copy2(W/'arxiv/main.pdf',S/'docs/paper/synthetic-players.pdf'); shutil.copy2(W/'synthetic-players-arxiv-source.zip',S/'docs/paper/synthetic-players-arxiv-source.zip')
(S/'docs/paper/synthetic-players.sha256').write_text('c5f153198eb7987d8fc2156902a412691d01188f38b5362c44f74c4f979c98f8  synthetic-players.pdf\n')
art={'repository':'yoheinakajima/synthetic-players','status':'final arXiv artifact','pages':19,'figures':5,'pdf_sha256':'c5f153198eb7987d8fc2156902a412691d01188f38b5362c44f74c4f979c98f8','source_sha256':'0b75e83583f58b2020feeee86ff999173a6d466be682a6b7471f950b36fdf0b1','markdown_sha256':'b6c8a95d5eba541d23256b36ab3a1c64c4d89a4db52f66762291bc9409d00dc4'}
(S/'docs/paper/synthetic-players-artifact.json').write_text(json.dumps(art,indent=2)+'\n')
bio=io.BytesIO()
with tarfile.open(fileobj=bio,mode='w') as t:
 for p in sorted(x for x in S.rglob('*') if x.is_file()):
  data=p.read_bytes(); i=tarfile.TarInfo(p.relative_to(S).as_posix()); i.size=len(data); i.mode=0o644; i.uid=i.gid=0; i.mtime=1785542400; t.addfile(i,io.BytesIO(data))
payload=gzip.compress(bio.getvalue(),compresslevel=9,mtime=0); b64=base64.b64encode(payload).decode(); out=R/'scripts/final_release_chunks'; shutil.rmtree(out,ignore_errors=True); out.mkdir(parents=True)
size=((len(b64)+9)//10+3)//4*4; chunks=[]
for n in range(10):
 s=b64[n*size:(n+1)*size]; p=out/f'payload-{n:02d}.txt'; p.write_text(s); chunks.append({'path':p.relative_to(R).as_posix(),'chars':len(s),'sha256':hashlib.sha256(s.encode()).hexdigest()})
manifest={'payload_sha256':hashlib.sha256(payload).hexdigest(),'payload_bytes':len(payload),'base64_chars':len(b64),'chunks':chunks,'canonical_artifacts':art}; (out/'payload-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
installer=f'''#!/usr/bin/env python3\nfrom pathlib import Path\nimport base64,hashlib,io,tarfile\nR=Path(__file__).resolve().parents[1]; P=R/'scripts/final_release_chunks'; raw=''.join(p.read_text().strip() for p in sorted(P.glob('payload-[0-9][0-9].txt'))); data=base64.b64decode(raw,validate=True); assert hashlib.sha256(data).hexdigest()=='{manifest['payload_sha256']}'\nwith tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as t:\n for m in t.getmembers(): q=(R/m.name).resolve(); assert q==R.resolve() or R.resolve() in q.parents\n t.extractall(R)\nprint('installed final release',hashlib.sha256(data).hexdigest())\n'''; (R/'scripts/install_final_release.py').write_text(installer)
shutil.rmtree(R/'scripts/final_release_transport',ignore_errors=True); (R/'.github/workflows/assemble-final-release-payload.yml').unlink(); (R/'scripts/recover_final_source.py').unlink(); (R/'scripts/build_final_chunks.py').unlink()
print(json.dumps(manifest,indent=2))
