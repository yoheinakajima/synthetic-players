#!/usr/bin/env python3
from __future__ import annotations
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'docs/paper/figures'; COLORS={'s2a':'#1f77b4','s2p':'#d95f02'}
rows=list(csv.DictReader((FIG/'prompt-indexed-delta.csv').open(newline='',encoding='utf-8')))
per=[r for r in rows if r['persona']!='aggregate']; agg={r['level']:r for r in rows if r['persona']=='aggregate'}
labels=[f'p{i:02d}' for i in range(1,17)]+['Fixed-panel aggregate']; y=np.arange(len(labels),dtype=float)
fig,ax=plt.subplots(figsize=(7.25,5.9))
for level,marker,offset,label in [('s2a','o',-0.27,'S2 absent'),('s2p','s',0.27,'S2 present')]:
    by={r['persona']:r for r in per if r['level']==level}; rec=[by[p] for p in labels[:-1]]
    d=np.array([float(r['delta']) for r in rec]); lo=np.array([float(r['lo95']) for r in rec]); hi=np.array([float(r['hi95']) for r in rec])
    ax.errorbar(d,y[:-1]+offset,xerr=[d-lo,hi-d],fmt=marker,color=COLORS[level],ecolor=COLORS[level],markersize=4.8,capsize=2.2,elinewidth=.9)
    s=agg[level]; point=float(s['delta']); lower=float(s['lo95']); upper=float(s['hi95'])
    ax.errorbar([point],[y[-1]+offset],xerr=[[point-lower],[upper-point]],fmt='D',color=COLORS[level],ecolor=COLORS[level],markersize=6.4,capsize=2.8,elinewidth=1.3)
ax.axvline(0,lw=.9,color='.35'); ax.axhline(15.5,lw=.7,color='.65'); ax.set_yticks(y,labels,fontsize=7.5); ax.get_yticklabels()[-1].set_fontweight('bold'); ax.invert_yaxis(); ax.set_xlim(-1.05,1.05); ax.set_xlabel(r'Observed prompt-indexed difference $\Delta_i$'); ax.set_title('Continuation-probability response by prompt configuration',loc='left',fontweight='bold')
ax.legend(handles=[Line2D([0],[0],marker='o',color=COLORS['s2a'],ls='none',label='S2 absent'),Line2D([0],[0],marker='s',color=COLORS['s2p'],ls='none',label='S2 present'),Line2D([0],[0],marker='D',color=COLORS['s2a'],ls='none',label='Aggregate (S2 absent)'),Line2D([0],[0],marker='D',color=COLORS['s2p'],ls='none',label='Aggregate (S2 present)')],frameon=False,loc='upper center',bbox_to_anchor=(.5,-.10),ncol=2,fontsize=8)
ax.grid(axis='x',alpha=.22); fig.subplots_adjust(top=.92,left=.15,right=.985,bottom=.21)
for ext in ('svg','pdf','png'): fig.savefig(FIG/f'prompt-indexed-delta.{ext}',bbox_inches='tight',dpi=240 if ext=='png' else None)
plt.close(fig)
print('generate_prompt_figure_v13: wrote dodged Figure 1 with wording-specific aggregate legend')
