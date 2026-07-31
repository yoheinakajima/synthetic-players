#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PAPER=ROOT/'docs/paper'; SOURCE=PAPER/'paper-draft.md'; HEADER=PAPER/'preprint-v13-header.tex'; OUTPUT=PAPER/'synthetic-players-preprint-v14.pdf'; SHA_FILE=PAPER/'synthetic-players-preprint-v14.sha256'; MANIFEST=PAPER/'synthetic-players-preprint-v14-artifact.json'; BUILD=ROOT/'.preprint-v14-build'; BUILD_MD=BUILD/'synthetic-players-preprint-v14.md'; FIGURES=('prompt-indexed-delta','condition-means','between-prompt-share','representation-effects','p13-audit')
def req(n):
    if shutil.which(n) is None: raise RuntimeError(f'required program not found: {n}')
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def prepare():
    lines=SOURCE.read_text(encoding='utf-8').splitlines(); title=lines[0][2:].strip().replace('"','\\"'); body='\n'.join(lines[1:]).lstrip(); body=re.sub(r'^\*\*Preprint v14.*?\n\n','',body,count=1,flags=re.S)
    for figure in FIGURES:
        body,n=re.subn(rf'!\[[^\]]*\]\(figures/{re.escape(figure)}\.svg\)',f'![](figures/{figure}.pdf){{width=95%}}',body,count=1)
        if n!=1: raise RuntimeError(f'expected one figure reference for {figure}, got {n}')
    # Defensive build-time de-duplication for the Phase 6 sentence previously duplicated in PDF output.
    sentence='A Phase 6 replication should preregister the primary/secondary hierarchy, candidate families, dependence units, maximum statistics, and cross-predicate error allocation before data collection.'
    body=body.replace(sentence+'\n\n'+sentence,sentence)
    body=body.replace('\n## References\n','\n## References\n\n\\begingroup\n\\small\n\\setlength{\\parskip}{0.32em}\n',1).rstrip()+'\n\n\\endgroup\n'; return title,body
def main():
    for x in ('pandoc','xelatex','pdfinfo','pdftotext'): req(x)
    title,body=prepare(); BUILD.mkdir(parents=True,exist_ok=True)
    BUILD_MD.write_text(f'''---
title: "{title}"
author: "Yohei Nakajima · Untapped Capital"
date: "July 2026"
lang: en-US
documentclass: article
classoption: [11pt, letterpaper]
geometry: [top=0.78in, bottom=0.82in, left=0.92in, right=0.92in]
fontsize: 11pt
linestretch: 1.10
colorlinks: true
linkcolor: "1F4E79"
urlcolor: "1F4E79"
---

{body}''',encoding='utf-8')
    subprocess.run(['pandoc',str(BUILD_MD),'--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex','--standalone','--pdf-engine=xelatex',f'--include-in-header={HEADER}',f'--resource-path={PAPER}:{ROOT}',f'--output={OUTPUT}'],cwd=ROOT,check=True)
    info=subprocess.check_output(['pdfinfo',str(OUTPUT)],cwd=ROOT,text=True); pages=int(next(x.split(':',1)[1].strip() for x in info.splitlines() if x.startswith('Pages:'))); digest=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(); SHA_FILE.write_text(f'{digest}  {OUTPUT.name}\n',encoding='utf-8'); MANIFEST.write_text(json.dumps({'repository':'yoheinakajima/synthetic-players','source_commit':git('rev-parse','HEAD'),'source':'docs/paper/paper-draft.md','pdf':'docs/paper/synthetic-players-preprint-v14.pdf','pdf_sha256':digest,'pages':pages,'workflow_run':os.environ.get('GITHUB_RUN_ID','local'),'status':'arXiv candidate v14'},indent=2)+'\n',encoding='utf-8')
    text=subprocess.check_output(['pdftotext',str(OUTPUT),'-'],cwd=ROOT,text=True); sentence='A Phase 6 replication should preregister the primary/secondary hierarchy'
    if text.count(sentence)!=1: raise RuntimeError(f'Phase 6 sentence count in PDF is {text.count(sentence)}, expected 1')
    print(info); print(f'build_preprint_pdf_v14: sha256={digest}'); return 0
if __name__=='__main__': raise SystemExit(main())
