#!/usr/bin/env python3
"""Bounded saved-count sensitivity; no DB/provider access or historical writes."""
from pathlib import Path
import csv,hashlib,json,math,platform,resource,socket,sys,time
resource.setrlimit(resource.RLIMIT_CPU,(240,240))
def deny(*a,**k):raise RuntimeError('network forbidden for saved-data sensitivity')
socket.socket.connect=deny;socket.socket.bind=deny
import numpy as np
import scipy
from scipy.stats import beta
J=Path(__file__).resolve().parents[1];R=J.parents[1]
planfile=J/'contrast-sensitivity-plan.json';plan=json.loads(planfile.read_text())
assert plan['draws_per_alpha']<=50000 and plan['bootstrap_draws']<=50000
started=time.process_time();wall=time.monotonic()
source=R/plan['source'];rows=list(csv.DictReader(source.open()))
by={(r['personaId'],r['cell']):r for r in rows};cells=['rep-d10-s2a','rep-d10-s2p','rep-d90-s2a','rep-d90-s2p']
counts={cell:np.array([[int(by[(f'p{i:02}',cell)][c]) for c in ('episodeCounts0','episodeCountsHalf','episodeCounts1')] for i in range(1,17)]) for cell in cells}
data={cell:np.array([np.repeat([0.,.5,1.],v) for v in counts[cell]]) for cell in cells}
summary={r['cell']:r for r in csv.DictReader((R/'docs/analysis/submission/figure-sources/variance-correction.csv').open())}
for cell in cells:
 assert counts[cell].shape==(16,3) and np.all(counts[cell].sum(axis=1)==6)
 assert abs(float(data[cell].mean())-float(summary[cell]['poolMean']))<.0000006
 for i in range(16):assert abs(data[cell][i].mean()-float(by[(f'p{i+1:02}',cell)]['mean']))<.0000006
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def seed(label):return (int.from_bytes(hashlib.sha256(label.encode()).digest()[:8],'big')^plan['base_seed'])%(2**63-1)
def stats(draws,mean,var):
 mean_mc=float(np.mean(draws));var_mc=float(np.var(draws,ddof=1));se=math.sqrt(var/len(draws))
 assert abs(mean_mc-mean)<=6*se+1e-12,(mean_mc,mean,se)
 assert abs(var_mc/var-1)<.08,(var_mc,var)
 lo,med,hi=np.quantile(draws,[.025,.5,.975])
 return {'lower':float(lo),'median':float(med),'upper':float(hi),'probability_positive':float(np.mean(draws>0)),'zero_excluded':bool(lo>0 or hi<0),'mc_mean':mean_mc,'analytic_mean':mean,'mc_variance':var_mc,'analytic_variance':var,'mc_mean_z':(mean_mc-mean)/se}
output={'plan_sha256':sha(planfile),'input_sha256':sha(source),'prepared_source_head':plan['prepared_source_head'],'seed_rule':plan['seed_rule'],'counts':{c:v.tolist() for c,v in counts.items()},'observed':{},'dirichlet':[],'two_stage_bootstrap':[],'cp_allocation':{},'execution_note':'First invocation stopped before any draws at overly strict equality against rounded CSV display means; validation tolerance corrected to half-unit in6decimal display precision, no seeds/draws/methods changed.', 'verification':'Source category totals, six episodes/prompt, independent frozen pool means and analytic moments checked; all planned outcomes retained'}
for level in ['s2a','s2p']:output['observed'][level]=float(data['rep-d90-'+level].mean()-data['rep-d10-'+level].mean())
for alpha in plan['alphas']:
 label=f'dirichlet:alpha={alpha:g}';rng=np.random.default_rng(seed(label));means={};variances={};draws={}
 for cell in cells:
  a=counts[cell]+alpha;total=a.sum(axis=1);mu=(.5*a[:,1]+a[:,2])/total
  # Independent scalar Dirichlet linear-functional formula (not simulation).
  second=(.25*a[:,1]+a[:,2])/total;vv=(second-mu*mu)/(total+1)
  means[cell]=float(mu.mean());variances[cell]=float(vv.sum()/16**2)
  draw=rng.dirichlet(a[0],size=plan['draws_per_alpha']);latent=.5*draw[:,1]+draw[:,2]
  for i in range(1,16):
   draw=rng.dirichlet(a[i],size=plan['draws_per_alpha']);latent+=.5*draw[:,1]+draw[:,2]
  draws[cell]=latent/16
 for level in ['s2a','s2p']:
  low='rep-d10-'+level;high='rep-d90-'+level
  output['dirichlet'].append({'alpha':alpha,'contrast':level,'draws':plan['draws_per_alpha'],'seed':seed(label),**stats(draws[high]-draws[low],means[high]-means[low],variances[high]+variances[low])})
for level in ['s2a','s2p']:
 label='bootstrap:'+level;rng=np.random.default_rng(seed(label));low=data['rep-d10-'+level];high=data['rep-d90-'+level];b=plan['bootstrap_draws'];all_draws=[]
 for start in range(0,b,1000):
  m=min(1000,b-start);pidx=rng.integers(0,16,size=(m,16));selected_low=low[pidx];selected_high=high[pidx]
  loidx=rng.integers(0,6,size=(m,16,6));hiidx=rng.integers(0,6,size=(m,16,6))
  all_draws.append((np.take_along_axis(selected_high,hiidx,axis=2)-np.take_along_axis(selected_low,loidx,axis=2)).mean(axis=(1,2)))
 vals=np.concatenate(all_draws);contrast_by_prompt=high.mean(axis=1)-low.mean(axis=1)
 var=(float(np.var(contrast_by_prompt,ddof=0))+float((np.var(high,axis=1,ddof=0)+np.var(low,axis=1,ddof=0)).mean()/6))/16
 output['two_stage_bootstrap'].append({'contrast':level,'draws':b,'seed':seed(label),**stats(vals,float(contrast_by_prompt.mean()),var)})
# Independent verification of actual four-component allocation for each aggregate contrast.
for level in ['s2a','s2p']:
 intervals={}
 for d in ['10','90']:
  cc=counts['rep-d'+d+'-'+level].sum(axis=0);n=int(cc.sum());bounds=[]
  for k in [int(cc[1]+cc[2]),int(cc[2])]:
   component_alpha=.05/4
   bounds.append([0. if k==0 else float(beta.ppf(component_alpha/2,k,n-k+1)),1. if k==n else float(beta.ppf(1-component_alpha/2,k+1,n-k))])
  intervals[d]=np.mean(bounds,axis=0).tolist()
 contrast=[intervals['90'][0]-intervals['10'][1],intervals['90'][1]-intervals['10'][0]]
 output['cp_allocation'][level]={'component_confidence':.9875,'condition_mean_minimum_working_model_confidence':.975,'contrast_minimum_working_model_confidence':.95,'simultaneous_scope':'four binary component-condition means within this one contrast only; not both contrasts or32rows','condition_intervals':intervals,'contrast_interval':contrast}
output['environment']={'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'cpu_seconds':time.process_time()-started,'wall_seconds':time.monotonic()-wall,'network':'socket connect/bind denied; no provider modules/DB access','source_only':'saved category counts; no modification to study/ledger/capsule'}
assert output['environment']['cpu_seconds']<240
(J/'contrast-sensitivity.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({k:output[k] for k in ['observed','dirichlet','two_stage_bootstrap','cp_allocation','environment']},indent=2))
