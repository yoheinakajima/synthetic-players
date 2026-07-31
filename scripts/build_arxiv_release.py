#!/usr/bin/env python3
"""Build the canonical PDF and a minimal arXiv-uploadable source archive."""
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAPER_DIR=ROOT/'docs/paper'; SOURCE=PAPER_DIR/'paper.md'; ALIAS=PAPER_DIR/'paper-draft.md'
OUTPUT=PAPER_DIR/'synthetic-players.pdf'; SHA_FILE=PAPER_DIR/'synthetic-players.sha256'; ARTIFACT=PAPER_DIR/'synthetic-players-artifact.json'; SOURCE_ZIP=PAPER_DIR/'synthetic-players-arxiv-source.zip'; METADATA=PAPER_DIR/'arxiv-metadata.txt'; ARXIV_DIR=ROOT/'arxiv'
FIGURES=('between-prompt-share','prompt-indexed-delta','condition-means','representation-effects','p13-audit')
PHASE6='A Phase 6 test will preregister the candidate family, episode-level dependence unit, interiority gate, maximum statistic, familywise decision rule, and sample size before any data are collected.'
ABSTRACT_END='The results concern one fixed model-prompt panel and do not establish human substitutability.'

def require(p):
    if not shutil.which(p): raise RuntimeError(f'required program not found: {p}')
def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip() if (ROOT/'.git').exists() else 'local'
def extract(text):
    tm=re.search(r'^# (.+)$',text,re.M); am=re.search(r'^## Abstract\n\n(.+?)(?=\n\n## 1\. Introduction)',text,re.M|re.S)
    if not tm or not am: raise RuntimeError('title or abstract missing')
    return tm.group(1).strip(),' '.join(am.group(1).split())
def yaml_quote(s): return s.replace('\\','\\\\').replace('"','\\"')
def prepare(text,title,abstract,out):
    body=text[text.index('## 1. Introduction'):]
    for f in FIGURES:
        body,n=re.subn(rf'!\[[^\]]*\]\(figures/{re.escape(f)}\.svg\)',lambda _m,x=f:f'![](figures/{x}.pdf){{width=95%}}',body,count=1)
        if n!=1: raise RuntimeError(f'expected one figure reference for {f}; got {n}')
    body=body.replace('\n## References\n','\n## References\n\n\\begingroup\n\\small\n\\setlength{\\parskip}{0.30em}\n',1).rstrip()+'\n\n\\endgroup\n'
    # Put the abstract in Pandoc metadata so LaTeX-special characters such as % are escaped.
    indented='\n'.join('  '+line for line in abstract.splitlines())
    out.write_text(f'''---
title: "{yaml_quote(title)}"
author: "Yohei Nakajima"
date: "Untapped Capital - July 2026"
abstract: |
{indented}
lang: en-US
documentclass: article
classoption: [11pt]
colorlinks: true
linkcolor: blue
urlcolor: blue
---

{body}''',encoding='utf-8')
def header(path):
    path.write_text(r'''\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{booktabs,longtable,array,ragged2e,graphicx,float,caption,xcolor,enumitem}
\usepackage{geometry}
\geometry{letterpaper,top=0.82in,bottom=0.86in,left=0.92in,right=0.92in}
\captionsetup{font=small,labelfont=bf}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.52em}
\setlength{\emergencystretch}{3em}
\setlist{nosep,leftmargin=*}
\AtBeginEnvironment{longtable}{\small}
\usepackage{newunicodechar}
\newunicodechar{δ}{\ensuremath{\delta}}
\newunicodechar{ρ}{\ensuremath{\rho}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{−}{\ensuremath{-}}
''',encoding='utf-8')
def compile(tex,cwd):
    for _ in range(2):
        r=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',tex.name],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if r.returncode: raise RuntimeError('pdflatex failed:\n'+r.stdout[-12000:])
def detzip(path,root,members):
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for m in sorted(members,key=lambda p:p.as_posix()):
            rel=m.relative_to(root).as_posix(); info=zipfile.ZipInfo(rel,date_time=(2026,7,31,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16; z.writestr(info,m.read_bytes())
def preflight(title,abstract,pdf,srczip):
    info=subprocess.check_output(['pdfinfo',str(pdf)],text=True); pages=int(next(x.split(':',1)[1].strip() for x in info.splitlines() if x.startswith('Pages:')))
    extracted=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True,errors='replace'); norm=' '.join(extracted.split()); errors=[]
    def compact(value): return re.sub(r'[^a-z0-9]+','',value.lower())
    required=(title,'4,916','0.011','63%-71%','47%-53%','+0.083','0/40 to 37/40','p13 is therefore a replication target rather than a finding',ABSTRACT_END,'Large language models can predict the results of social science experiments')
    for m in required:
        if ' '.join(m.split()) not in norm: errors.append(f'PDF text missing {m!r}')
    if compact(abstract) not in compact(extracted): errors.append('complete abstract not recoverable from PDF text')
    if not 16<=pages<=28: errors.append(f'unexpected page count {pages}')
    if norm.count('A Phase 6 test will preregister the candidate family')!=1: errors.append('Phase 6 sentence count not one')
    for f in ('Preprint v','working draft','review candidate','arXiv candidate'):
        if f.lower() in norm.lower(): errors.append(f'release label remains: {f}')
    if len(abstract)>1920 or not abstract.isascii(): errors.append(f'abstract invalid chars={len(abstract)} ascii={abstract.isascii()}')
    fonts=subprocess.check_output(['pdffonts',str(pdf)],text=True)
    for line in fonts.splitlines()[2:]:
        cols=line.split()
        if len(cols)>=7 and (cols[-5].lower()!='yes' or cols[-4].lower()!='yes'): errors.append(f'font not embedded/subset: {line}')
    with zipfile.ZipFile(srczip) as z:
        expected=sorted(['main.tex']+[f'figures/{x}.pdf' for x in FIGURES])
        if sorted(z.namelist())!=expected: errors.append(f'arXiv source members differ: {z.namelist()}')
    if errors: raise RuntimeError('release preflight failed:\n- '+'\n- '.join(errors))
    return pages,info,fonts

def main():
    for p in ('pandoc','pdflatex','pdfinfo','pdftotext','pdffonts'): require(p)
    text=SOURCE.read_text(encoding='utf-8')
    if ALIAS.read_bytes()!=SOURCE.read_bytes(): raise RuntimeError('paper aliases differ')
    if text.count(PHASE6)!=1: raise RuntimeError('Phase 6 exact sentence count must be one')
    for f in ('Preprint v','working draft','review candidate','arXiv candidate'):
        if f.lower() in text.lower(): raise RuntimeError(f'release label in source: {f}')
    title,abstract=extract(text)
    if not abstract.endswith(ABSTRACT_END): raise RuntimeError('abstract ending missing')
    if ARXIV_DIR.exists(): shutil.rmtree(ARXIV_DIR)
    figs=ARXIV_DIR/'figures'; figs.mkdir(parents=True)
    for f in FIGURES: shutil.copy2(PAPER_DIR/'figures'/f'{f}.pdf',figs/f'{f}.pdf')
    with tempfile.TemporaryDirectory(prefix='synthetic-players-arxiv-') as td:
        temp=Path(td); md=temp/'manuscript.md'; h=temp/'header.tex'; prepare(text,title,abstract,md); header(h); tex=ARXIV_DIR/'main.tex'
        subprocess.run(['pandoc',str(md),'--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex','--to=latex','--standalone','--include-in-header',str(h),'--metadata','pdfauthor=Yohei Nakajima','-o',str(tex)],cwd=ROOT,check=True)
        tex.write_text('\\pdfoutput=1\n'+tex.read_text(encoding='utf-8'),encoding='utf-8')
    compile(ARXIV_DIR/'main.tex',ARXIV_DIR); shutil.copy2(ARXIV_DIR/'main.pdf',OUTPUT)
    for s in ('.aux','.log','.out','.toc','.pdf'):
        x=ARXIV_DIR/f'main{s}'
        if x.exists(): x.unlink()
    detzip(SOURCE_ZIP,ARXIV_DIR,[ARXIV_DIR/'main.tex']+[figs/f'{x}.pdf' for x in FIGURES])
    pages,info,fonts=preflight(title,abstract,OUTPUT,SOURCE_ZIP)
    digest=hashlib.sha256(OUTPUT.read_bytes()).hexdigest(); sdigest=hashlib.sha256(SOURCE_ZIP.read_bytes()).hexdigest(); SHA_FILE.write_text(f'{digest}  {OUTPUT.name}\n')
    METADATA.write_text(f'Title: {title}\nAuthor: Yohei Nakajima\nSuggested primary category: cs.AI\nSuggested cross-list: cs.HC\nComments: {pages} pages, 5 figures. Code, data, registrations, review record, and zero-call replay capsule: https://github.com/yoheinakajima/synthetic-players\n\nAbstract:\n{abstract}\n',encoding='ascii')
    ARTIFACT.write_text(json.dumps({'repository':'yoheinakajima/synthetic-players','source_commit':git('rev-parse','HEAD'),'source':'docs/paper/paper.md','pdf':'docs/paper/synthetic-players.pdf','pdf_sha256':digest,'arxiv_source':'docs/paper/synthetic-players-arxiv-source.zip','arxiv_source_sha256':sdigest,'pages':pages,'figures':5,'workflow_run':os.environ.get('GITHUB_RUN_ID','local'),'status':'arXiv-ready preprint'},indent=2)+'\n')
    print(info); print(f'build_arxiv_release: pdf_sha256={digest} source_sha256={sdigest}')
if __name__=='__main__': main()
