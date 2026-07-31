#!/usr/bin/env python3
from pathlib import Path
import urllib.request
P=Path(__file__).resolve().parents[1]/'docs/paper/paper-draft.md'
text=P.read_text(encoding='utf-8')
required={
'10.1038/s41586-026-10742-x':'Large language models can predict the results of social science experiments',
'10.18653/v1/2026.findings-acl.1316':'Beyond fixed psychological personas: State beats trait, but language models are state-blind',
'10.1609/aies.v8i1.36553':'Whose personae? Synthetic persona experiments in LLM research and pathways to transparency',
'10.1177/00491241251330582':'Machine bias: How do generative language models answer opinion polls?',
'arXiv.2602.15785':'This human study did not involve human subjects: Validating LLM simulations as behavioral evidence',
'arXiv.2603.19167':'Evaluating counterfactual strategic reasoning in large language models',
'arXiv.2604.24698':'The chameleon’s limit: Investigating persona collapse and homogenization in large language models',
'arXiv.2605.20767':'The illusion of intervention: Your LLM-simulated experiment is an observational study',
'arXiv.2607.19670':'Same game, different story: A minimal conservative strategic robustness benchmark for large language model agents',
'arXiv.2411.10109':'Generative agent simulations of 1,000 people',
'10.1038/s41562-025-02172-y':'Playing repeated games with large language models',
}
errors=[]
for ident,title in required.items():
    if ident not in text or title.lower() not in text.lower(): errors.append(f'missing verified pair: {ident} / {title}')
for bad in ('s41586-026-10385-0','2026.findings-acl.1302','00491241251343947','LLMs should not replace human participants','Nature Human Behaviour, 9*, 215–228'):
    if bad in text: errors.append(f'known regressed metadata remains: {bad}')
# Live checks use primary endpoints that permit automated retrieval. Publisher endpoints
# known to return bot-blocking 403/connection resets remain protected by the exact
# metadata-pair and known-regression assertions above.
urls=[
'https://www.nature.com/articles/s41586-026-10742-x',
'https://aclanthology.org/2026.findings-acl.1316/',
'https://arxiv.org/abs/2602.15785',
'https://arxiv.org/abs/2603.19167',
'https://arxiv.org/abs/2604.24698',
'https://arxiv.org/abs/2605.20767',
'https://arxiv.org/abs/2607.19670',
'https://arxiv.org/abs/2411.10109',
'https://www.nature.com/articles/s41562-025-02172-y',
'https://proceedings.mlr.press/v267/anthis25a.html',
]
for url in urls:
    req=urllib.request.Request(url,headers={'User-Agent':'synthetic-players-reference-lint/1.0'})
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            if r.status>=400: errors.append(f'{url}: HTTP {r.status}')
    except Exception as e: errors.append(f'{url}: {e}')
if errors:
    raise SystemExit('reference lint failed:\n- '+'\n- '.join(errors))
print(f'reference lint: PASS ({len(required)} verified metadata pairs; {len(urls)} retrievable primary URLs resolved)')
