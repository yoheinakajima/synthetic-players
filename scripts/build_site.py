#!/usr/bin/env python3
"""Assemble the GitHub Pages artifact from committed site sources and paper assets."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site'
OUT = ROOT / '_site'
PAPER = ROOT / 'docs' / 'paper'
FIGURES = ('between-prompt-share', 'prompt-indexed-delta', 'condition-means', 'representation-effects', 'p13-audit')

if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(SOURCE, OUT)
(OUT / '.nojekyll').write_text('', encoding='utf-8')
shutil.copy2(PAPER / 'synthetic-players.pdf', OUT / 'paper.pdf')
shutil.copy2(PAPER / 'synthetic-players-arxiv-source.zip', OUT / 'arxiv-source.zip')
assets = OUT / 'assets'
assets.mkdir(exist_ok=True)
for name in FIGURES:
    shutil.copy2(PAPER / 'figures' / f'{name}.png', assets / f'{name}.png')
for required in ('index.html', 'styles.css', 'paper.pdf', 'arxiv-source.zip', '.nojekyll'):
    path = OUT / required
    if not path.exists() or (path.name != '.nojekyll' and path.stat().st_size == 0):
        raise RuntimeError(f'missing site artifact: {path}')
print(f'build_site: {OUT}')
