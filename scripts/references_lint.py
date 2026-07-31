#!/usr/bin/env python3
"""Guard retrieval-backed bibliography metadata against regression."""
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / 'docs' / 'paper' / 'paper.md'
if not PAPER.exists():
    PAPER = ROOT / 'docs' / 'paper' / 'paper-draft.md'
text = PAPER.read_text(encoding='utf-8')

required = {
    '10.1038/s41586-026-10742-x': 'Large language models can predict the results of social science experiments',
    '10.18653/v1/2026.findings-acl.1316': 'Beyond fixed psychological personas: State beats trait, but language models are state-blind',
    '10.1609/aies.v8i1.36553': 'Whose personae? Synthetic persona experiments in LLM research and pathways to transparency',
    '10.1177/00491241251330582': 'Machine bias: How do generative language models answer opinion polls?',
    'arXiv.2602.15785': 'This human study did not involve human subjects: Validating LLM simulations as behavioral evidence',
    'arXiv.2603.19167': 'Evaluating counterfactual strategic reasoning in large language models',
    'arXiv.2604.24698': 'The chameleon’s limit: Investigating persona collapse and homogenization in large language models',
    'arXiv.2605.20767': 'The illusion of intervention: Your LLM-simulated experiment is an observational study',
    'arXiv.2607.19670': 'Same game, different story: A minimal conservative strategic robustness benchmark for large language model agents',
    'arXiv:2411.10109v3': 'LLM agents grounded in self-reports enable general-purpose simulation of individuals',
    '10.1038/s41562-025-02172-y': 'Playing repeated games with large language models',
}
required_fragments = (
    'Park, J. S., Zou, C. Q., Kamphorst, J., Egan, N., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., Liang, P., Willer, R., and Bernstein, M. S.',
    'Akata, E., Schulz, L., Coda-Forno, J., Oh, S. J., Bethge, M., and Schulz, E.',
)
known_bad = (
    's41586-026-10385-0',
    '2026.findings-acl.1302',
    '00491241251343947',
    'LLMs should not replace human participants',
    'Nature Human Behaviour, 9*, 215–228',
    'Generative agent simulations of 1,000 people',
)
errors = []
for identifier, title in required.items():
    if identifier not in text or title.lower() not in text.lower():
        errors.append(f'missing verified pair: {identifier} / {title}')
for fragment in required_fragments:
    if fragment not in text:
        errors.append(f'missing verified author fragment: {fragment}')
for bad in known_bad:
    if bad in text:
        errors.append(f'known regressed or superseded metadata remains: {bad}')

# Live checks use primary endpoints that permit automated retrieval. Publisher endpoints
# known to return bot-blocking responses remain protected by exact-pair assertions above.
urls = (
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
)
for url in urls:
    request = urllib.request.Request(url, headers={'User-Agent': 'synthetic-players-reference-lint/2.0'})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status >= 400:
                errors.append(f'{url}: HTTP {response.status}')
    except Exception as exc:
        errors.append(f'{url}: {exc}')

if errors:
    raise SystemExit('reference lint failed:\n- ' + '\n- '.join(errors))
print(f'reference lint: PASS ({len(required)} verified metadata pairs; {len(urls)} primary URLs resolved)')
