#!/usr/bin/env python3
"""Fixed-panel symmetric-Dirichlet prior sensitivity for between-prompt composition."""
from __future__ import annotations
import csv, hashlib, json, os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/analysis/submission/figure-sources/episode-cluster-cells.csv'
OUTDIR=ROOT/'docs/analysis/submission/final'
OUTDIR.mkdir(parents=True,exist_ok=True)
OUTJSON=OUTDIR/'composition-prior-sensitivity.json'
OUTCSV=OUTDIR/'composition-prior-sensitivity.csv'
OUTMD=OUTDIR/'composition-prior-sensitivity.md'
DRAWS=int(os.environ.get('FINAL_PRIOR_DRAWS','200000'))
BASE_SEED=20260731
ALPHAS=(0.25,0.5,1.0)
CELLS=('rep-d10-s2a','rep-d10-s2p','rep-d90-s2a','rep-d90-s2p')

def seed(label:str)->int:
    return (int.from_bytes(hashlib.sha256(label.encode()).digest()[:8],'big') ^ BASE_SEED) % (2**63-1)

def q(arr):
    return [float(x) for x in np.quantile(np.asarray(arr),[.025,.5,.975])]

def main():
    rows=list(csv.DictReader(SOURCE.open(newline='',encoding='utf-8')))
    counts={(r['personaId'],r['cell']):np.array([r['episodeCounts0'],r['episodeCountsHalf'],r['episodeCounts1']],float) for r in rows}
    output=[]
    for alpha in ALPHAS:
        for cell in CELLS:
            rng=np.random.default_rng(seed(f'{alpha}:{cell}'))
            shares=[]
            for start in range(0,DRAWS,2500):
                n=min(2500,DRAWS-start)
                probs=np.stack([rng.dirichlet(counts[(f'p{i:02d}',cell)]+alpha,size=n) for i in range(1,17)],axis=1)
                means=.5*probs[:,:,1]+probs[:,:,2]
                second=.25*probs[:,:,1]+probs[:,:,2]
                within=second-means**2
                between=np.var(means,axis=1,ddof=1)
                shares.extend((between/(between+np.mean(within,axis=1))).tolist())
            lo,med,hi=q(shares)
            output.append({'alpha':alpha,'cell':cell,'draws':DRAWS,'seed':seed(f'{alpha}:{cell}'),'shareLo95':lo,'shareMedian':med,'shareHi95':hi,'probShareAboveHalf':float(np.mean(np.asarray(shares)>.5))})
    payload={'status':'post-adjudication zero-call prior sensitivity','symmetricDirichletAlphas':list(ALPHAS),'rows':output}
    OUTJSON.write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    with OUTCSV.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(output[0]));w.writeheader();w.writerows(output)
    lines=['# Fixed-panel composition prior sensitivity','', '> **STATUS: POST-ADJUDICATION, ZERO-CALL SENSITIVITY.** The exact sixteen prompts remain fixed. Each prompt-cell outcome distribution receives a symmetric Dirichlet(alpha, alpha, alpha) prior over {0, 0.5, 1}.','', '| alpha | cell | median between share | 95% interval | Pr(share > 0.5) |','|---:|---|---:|---:|---:|']
    for r in output:
        lines.append(f"| {r['alpha']:.2f} | {r['cell']} | {r['shareMedian']:.3f} | [{r['shareLo95']:.3f}, {r['shareHi95']:.3f}] | {r['probShareAboveHalf']:.3f} |")
    lines += ['', 'The qualitative claim of substantial between-prompt composition survives across the sweep, but the stronger claim that the between share exceeds one-half is prior-sensitive under the symmetric alpha=1 sensitivity. The manuscript therefore treats dominance as prior-dependent rather than as a prior-robust finding.']
    OUTMD.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    summary_path=ROOT/'docs/analysis/submission/submission-analysis-summary.json'
    if summary_path.exists():
        summary=json.loads(summary_path.read_text(encoding='utf-8'))
        summary['compositionPriorSensitivity']=payload
        summary_path.write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output,indent=2))
if __name__=='__main__': main()
