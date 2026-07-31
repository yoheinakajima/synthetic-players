#!/usr/bin/env python3
"""Create the canonical, unversioned manuscript from the review-lineage source."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'docs' / 'paper' / 'paper-draft.md'
OUT = ROOT / 'docs' / 'paper' / 'paper.md'

ABSTRACT = (
    "Large language models are increasingly used as synthetic research participants and are often validated by whether their marginal responses resemble human data. "
    "We study a fixed panel of sixteen lightweight persona-conditioned GPT-4.1 configurations in repeated strategic games. The panel passed preregistered broad-reference checks in three of four repeated-game cells. "
    "A fixed-panel Dirichlet-Jeffreys sensitivity places median between-prompt shares of episode-level variation at 63%-71% (95% intervals 49%-81%); finite-opportunity plug-in estimates are 85%-96%. "
    "Aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative simultaneous 95% intervals [-0.171, +0.330] and [-0.181, +0.330]. "
    "The treatment changed both continuation probability and its textual representation, so incentive and framing channels remain undecomposed. "
    "Separate representation experiments found that replacing and repositioning one sentence shifted cooperation from 0/40 to 37/40 in a bare configuration, and that a displayed label or learned label-linked prior could override payoff dominance in one conflict cell. "
    "External review exposed family-error, dependence, and boundary-uncertainty defects; zero-call reanalysis changed the interpretation while preserving the historical record. "
    "A public capsule verifies 4,916 confirmatory Phase 3-5 runs with no live model calls. The results concern one model-prompt panel, use protocol-nonmatched human references, and do not establish human substitutability."
)

text = SRC.read_text(encoding='utf-8')
lines = text.splitlines()
if not lines or not lines[0].startswith('# '):
    raise SystemExit('paper title missing')
title = lines[0]
try:
    abstract_idx = lines.index('## Abstract')
except ValueError as exc:
    raise SystemExit('Abstract heading missing') from exc
prefix = [
    title,
    '',
    '**Yohei Nakajima**  ',
    'Untapped Capital',
    '',
    '**Open materials:** [project site](https://yoheinakajima.github.io/synthetic-players/) · [repository](https://github.com/yoheinakajima/synthetic-players) · [reproduction capsule](https://github.com/yoheinakajima/synthetic-players/tree/main/capsule)',
    '',
    '---',
    '',
]
body = '\n'.join(lines[abstract_idx:])
body = re.sub(
    r'(## Abstract\n\n).*?(?=\n\n## 1\. Introduction)',
    lambda match: match.group(1) + ABSTRACT,
    body,
    count=1,
    flags=re.S,
)
phase6 = (
    'A Phase 6 test will preregister the candidate family, episode-level dependence unit, '
    'interiority gate, maximum statistic, familywise decision rule, and sample size before any data are collected.'
)
while body.count(phase6) > 1:
    body = body.replace(phase6 + ' ' + phase6, phase6)
    body = body.replace(phase6 + '\n\n' + phase6, phase6)
body = body.replace(
    'Venue-specific AI-assistance language will be conformed at submission.',
    'AI systems are not listed as authors. Their roles as research apparatus and adversarial reviewers are disclosed here and in the public review record; the human author accepts responsibility for every claim.',
)
body = body.replace('mechanical v11→v12 disposition matrix', 'mechanical review disposition matrices')
old_park = (
    'Park, J. S., Zou, C. Q., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., Willer, R., Liang, P., and Bernstein, M. S. (2024). '
    'Generative agent simulations of 1,000 people. arXiv:2411.10109. https://doi.org/10.48550/arXiv.2411.10109'
)
new_park = (
    'Park, J. S., Zou, C. Q., Kamphorst, J., Egan, N., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., Liang, P., Willer, R., and Bernstein, M. S. (2024, revised 2026). '
    'LLM agents grounded in self-reports enable general-purpose simulation of individuals. arXiv:2411.10109v3. https://doi.org/10.48550/arXiv.2411.10109'
)
if old_park in body:
    body = body.replace(old_park, new_park)
elif new_park not in body:
    raise SystemExit('Park reference anchor missing')
for forbidden in ('Preprint v14', 'arXiv candidate', 'review candidate', 'working draft'):
    if forbidden.lower() in (title + '\n' + body).lower():
        raise SystemExit(f'forbidden release label remains: {forbidden}')
if body.count(phase6) != 1:
    raise SystemExit(f'Phase 6 sentence count is {body.count(phase6)}, expected 1')
if len(ABSTRACT) > 1920 or not ABSTRACT.isascii():
    raise SystemExit(f'abstract metadata invalid: chars={len(ABSTRACT)}, ascii={ABSTRACT.isascii()}')
final = '\n'.join(prefix) + body.rstrip() + '\n'
OUT.write_text(final, encoding='utf-8')
SRC.write_text(final, encoding='utf-8')
print(f'prepare_arxiv_release: {len(ABSTRACT)} abstract characters; canonical aliases synchronized')
