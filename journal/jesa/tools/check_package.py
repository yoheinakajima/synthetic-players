#!/usr/bin/env python3
"""Portable integrity/content checks; does not access network or providers."""
from pathlib import Path
import hashlib,json,re,subprocess,zipfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[3];J=R/'journal/jesa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=json.loads((J/'evidence-manifest.json').read_text())
for row in base['files']:
 assert sha(R/row['path'])==row['sha256'],f'baseline altered: {row["path"]}'
assert (J/'evidence/registry.json').read_bytes()==(R/'artifacts/api-server/prompts/registry.json').read_bytes()
assert (J/'evidence/personas-v4.json').read_bytes()==(R/'docs/phase5/personas-v4.json').read_bytes()
counts=json.loads((J/'word-count.json').read_text());assert counts['abstract']<=150 and counts['inclusive_conservative']<=5000
assert counts['all_source_tokens']==len((J/'manuscript.md').read_text().split())
audit=json.loads((J/'reference-audit.json').read_text());assert len(audit['rows'])==39 and sum(x['original37'] for x in audit['rows'])==37
main=(J/'manuscript.md').read_text();sup=(J/'supplement.md').read_text();maintext,mainrefs=main.split('\n## References\n',1)
for ref in json.loads((J/'references.json').read_text()):
 assert ref in sup,ref
for ref in [r for r in mainrefs.strip().split('\n\n') if r]:
 surname=ref.split(',')[0]
 assert surname in maintext,ref
assert 'Li, Y., and Ji, X.' not in main+sup and 'Persson, E.,' not in main+sup
for s in ('[−0.171, +0.330]','[−0.181, +0.330]','[.071,.189]','[.182,.231]','.075040','model-based simultaneous intervals','Under the pooled component-binomial working model','replication target','not a probability sample'):
 assert s in main,s
assert not re.search(r'§[47]|Appendix A\.3',sup),'stale supplementary cross-reference'
meta=json.loads((J/'author-metadata.json').read_text())
assert meta['sole_author']=='Yohei Nakajima' and meta['corresponding_email']=='yohei@untapped.vc'
value=0
for digit in meta['orcid'].replace('-','')[:-1]:value=(value+int(digit))*2
assert str((12-value%11)%11)==meta['orcid'][-1]
for name in ('manuscript.md','supplement.md','data-instructions.md'):
 text=(J/name).read_text()
 for value in ('Bellevue, Washington, USA','yohei@untapped.vc','0009-0009-1293-6053','Explore Science'):
  assert value in text,(name,value)
 for stale in ('await author confirmation','must not be submitted with unresolved','AUTHOR TO CONFIRM','final approval pending'):
  assert stale not in text,(name,stale)
assert meta['funding'] in main
history=json.loads((J/'tool-use-reconstruction.json').read_text())
assert history['baseline_commit']=='62ab90beff1d291b069c87f13b6b6b3495171ddd'
for row in history['pinned_files']:assert sha(R/row['path'])==row['sha256']
tasks=json.loads((J/'task-dispositions.json').read_text())['tasks']
assert [r['id'] for r in tasks]==[f'MARGINAL-{i:03}' for i in range(1,35)]
with zipfile.ZipFile(J/'jesa-source.zip') as source_zip:
 assert len(source_zip.namelist())==len(set(source_zip.namelist()))
 for name in source_zip.namelist():assert source_zip.read(name)==(J/name).read_bytes(),('source archive',name)
# All original figures are exact copies; count source assets separately from PDF inclusion.
for f in (J/'figures').glob('*.pdf'):assert sha(f)==sha(R/'arxiv/figures'/f.name)
receipt=json.loads((J/'evidence/receipt.json').read_text());t=receipt['reports'];c=receipt['counts']
assert c['total_verifier_runs']==t['phase3']['llmRuns']+t['phase3']['baselineRuns']+t['phase4']['replayedObservations']+t['phase5']['runs']==4919
assert c['confirmatory_runs']==c['total_verifier_runs']-c['legacy_diagnostic_runs']==4916
assert c['verifier_llm_runs_including_legacy']==c['total_verifier_runs']-c['deterministic_baselines']==4899
assert receipt['manifest_files_checked_before_and_after']==190 and receipt['network_attempts']==receipt['listening_ports']==receipt['provider_construction']==0
# Check every PDF word against page edges and text margins; no screenshot-only clearance.
ns={'p':'http://www.w3.org/1999/xhtml'};bounds=[]
for name in ('manuscript','supplement','data-instructions'):
 xml=subprocess.check_output(['pdftotext','-bbox',str(J/(name+'.pdf')),'-'],text=True)
 root=ET.fromstring(xml);bad=[]
 for num,page in enumerate(root.findall('.//p:page',ns),1):
  width=float(page.attrib['width']);height=float(page.attrib['height'])
  for word in page.findall('.//p:word',ns):
   a=word.attrib;x0=float(a['xMin']);x1=float(a['xMax']);y0=float(a['yMin']);y1=float(a['yMax'])
   if x0<69 or x1>width-69 or y0<50 or y1>height-30:
    bad.append({'page':num,'text':word.text,'box':[x0,y0,x1,y1]})
 assert not bad, (name,bad[:12])
 log=(J/(name+'.log')).read_text()
 assert 'Overfull' not in log and 'Missing character' not in log,(name,'TeX layout warnings')
 bounds.append({'pdf':name+'.pdf','pages':len(root.findall('.//p:page',ns)),'word_margin_violations':len(bad)})
if (J/'package-manifest.json').exists():
 manifest=json.loads((J/'package-manifest.json').read_text())
 for row in manifest['files']:assert sha(J/row['path'])==row['sha256'],f'candidate altered: {row["path"]}'
print(json.dumps({'verdict':'PASS','baseline_files_unchanged':len(base['files']),'references':39,'count':counts['inclusive_conservative'],'pdf_bounds':bounds,'replay':'count-derived/native logic/190 checksums/no network'},indent=2))
