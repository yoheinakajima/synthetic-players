#!/usr/bin/env python3
from pathlib import Path
import base64,gzip,hashlib,zlib
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
R=Path.cwd(); T=R/'scripts/final_release_transport'; W=Path('/tmp/final-release'); W.mkdir(exist_ok=True)
raw=''.join(p.read_text().strip() for p in sorted((R/'scripts/final_release_chunks').glob('payload-*.txt')))
gz=base64.b64decode(raw,validate=True); d=zlib.decompressobj(16+zlib.MAX_WBITS); tb=d.decompress(gz)
wanted={
'arxiv/main.tex':'746fd4929eb715e071833c0291e6ea65decb78eff4b2894f7b9b690abfa3da7a',
'arxiv/figures/between-prompt-share.pdf':'c352dea32a034758cd4aa8fa8581dcef3aaa61debf461c483641e05d74e8270b',
'arxiv/figures/condition-means.pdf':'1a991f1d74982b57487394763d971143434ab2d2dc00cd42c0a62edc946e689c',
'arxiv/figures/p13-audit.pdf':'d52ca52eb1d8ac8e58b1bc18dfb57b1a78f127ada973d1679fb898dea353fdbe',
'arxiv/figures/prompt-indexed-delta.pdf':'1cf2a5533b021858921ce2acb2501eb4931bad1f4d3ae81250a2ce42f187376a',
'arxiv/figures/representation-effects.pdf':'2931b724a72093fc0b4433cbae511107bd8aa8c70a20965ef522fb39f24d37ff'}
found={}; off=0
while off+512<=len(tb):
 h=tb[off:off+512]
 if h==b'\0'*512 or not h[257:263].startswith(b'ustar'): break
 name=h[:100].split(b'\0',1)[0].decode(); size=int((h[124:136].rstrip(b'\0 ').strip() or b'0'),8)
 data=tb[off+512:off+512+size]
 if name in wanted and len(data)==size:
  assert hashlib.sha256(data).hexdigest()==wanted[name]
  p=W/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data); found[name]=1
 off+=512+((size+511)//512)*512
assert set(found)==set(wanted),set(wanted)-set(found)
mraw=''.join(p.read_text().strip() for p in sorted(T.glob('md-*.txt'))); assert len(mraw)==32236
mgz=base64.b64decode(mraw,validate=True); assert hashlib.sha256(mgz).hexdigest()=='a5e8c06a88467e97f79a8a5d4c79b150a35e25f52a4cc6b97d457a929d4ca7f6'
md=gzip.decompress(mgz); assert hashlib.sha256(md).hexdigest()=='b6c8a95d5eba541d23256b36ab3a1c64c4d89a4db52f66762291bc9409d00dc4'; (W/'paper.md').write_bytes(md)
order=['main.tex','figures/between-prompt-share.pdf','figures/condition-means.pdf','figures/p13-audit.pdf','figures/prompt-indexed-delta.pdf','figures/representation-effects.pdf']
zpath=W/'synthetic-players-arxiv-source.zip'
with ZipFile(zpath,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
 for n in order:
  i=ZipInfo(n,(2026,8,1,0,0,0)); i.compress_type=ZIP_DEFLATED; i.create_system=3; i.external_attr=0o644<<16
  z.writestr(i,(W/'arxiv'/n).read_bytes(),compress_type=ZIP_DEFLATED,compresslevel=6)
assert hashlib.sha256(zpath.read_bytes()).hexdigest()=='0b75e83583f58b2020feeee86ff999173a6d466be682a6b7471f950b36fdf0b1'
print('canonical source and Markdown recovered')
