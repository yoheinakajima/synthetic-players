#!/usr/bin/env python3
"""Validate and synchronize the canonical, unversioned manuscript aliases."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
PAPER=ROOT/'docs/paper/paper.md'; ALIAS=ROOT/'docs/paper/paper-draft.md'
text=PAPER.read_text(encoding='utf-8')
if not text.startswith('# '): raise SystemExit('paper title missing')
m=re.search(r'^## Abstract\n\n(.+?)(?=\n\n## 1\. Introduction)',text,re.M|re.S)
if not m: raise SystemExit('abstract missing')
abstract=' '.join(m.group(1).split())
required=('0.011 below the lower reference bound','63%-71% under Jeffreys alpha=0.5 and 47%-53% under alpha=1','+0.083 and +0.078','0/40 to 37/40','p13 is therefore a replication target rather than a finding','A public capsule verifies 4,916 confirmatory Phase 3-5 runs','do not establish human substitutability')
errors=[x for x in required if x not in abstract]
for forbidden in ('Preprint v','working draft','review candidate','arXiv candidate'):
    if forbidden.lower() in text.lower(): errors.append(f'forbidden release label: {forbidden}')
if len(abstract)>1920 or not abstract.isascii(): errors.append(f'abstract metadata invalid: chars={len(abstract)}, ascii={abstract.isascii()}')
if errors: raise SystemExit('canonical manuscript validation failed:\n- '+'\n- '.join(errors))
ALIAS.write_text(text,encoding='utf-8')
print(f'prepare_arxiv_release: canonical aliases synchronized; abstract={len(abstract)} chars')
