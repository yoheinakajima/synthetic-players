#!/usr/bin/env python3
"""Read-only metadata aggregation over a disposable released DB; no completions copied."""
import collections,datetime,hashlib,json,pathlib,sqlite3,sys
source=pathlib.Path(sys.argv[1]).resolve();dest=pathlib.Path(sys.argv[2]).resolve()
c=sqlite3.connect('file:'+str(source)+'?mode=ro',uri=True)
# Two linear scans avoid a large unindexed self-join over event payloads.
q="SELECT run_id,id,timestamp,payload FROM events WHERE type='llm.requested'"
responses={(run,rid):json.loads(p) for run,rid,p in c.execute("SELECT run_id,caused_by,payload FROM events WHERE type='llm.responded'")}
rows={}
for run_id,request_id,timestamp,req in c.execute(q):
 res=responses.get((run_id,request_id));r=res or {}
 p=json.loads(req);arm=p.get('armId','');phase='phase5' if arm.startswith('p5-') else 'phase4' if arm else 'legacy-phase3'
 key=(phase,json.dumps(p.get('model','not-recorded'),sort_keys=True),json.dumps(p.get('providerRoute','not-recorded'),sort_keys=True))
 x=rows.setdefault(key,{'phase':phase,'requested_model':json.loads(key[1]),'provider_route':json.loads(key[2]),'first_recorded_request_utc':timestamp,'last_recorded_request_utc':timestamp,'request_events':0,'response_events':0,'returned_models':collections.Counter(),'provider_created_unix_range':None})
 x['first_recorded_request_utc']=min(timestamp,x['first_recorded_request_utc']);x['last_recorded_request_utc']=max(timestamp,x['last_recorded_request_utc']);x['request_events']+=1
 if res:
  x['response_events']+=1;x['returned_models'][r.get('model','not-recorded')]+=1
  created=r.get('provider_meta',{}).get('created')
  if isinstance(created,(int,float)):
   prev=x['provider_created_unix_range'];x['provider_created_unix_range']=[min(prev[0],created),max(prev[1],created)] if prev else [created,created]
assert sum(r['request_events'] for r in rows.values())==36251
assert sum(r['response_events'] for r in rows.values())==36227
assert sum(r['request_events']-r['response_events'] for r in rows.values())==24
out={'source':'released capsule/data/engine.db.xz, decompressed disposable copy','decompressed_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'query':q,'scope':'all ordinary requested events, including legacy diagnostics and failed-run partials; not confirmatory-only or ledger call accounting','rows':list(rows.values()),'limits':'Recorded request timestamps may be empty; missing values do not establish collection windows. Provider-created Unix ranges, where present, are provider metadata only. Model names/routes are archive metadata, not provider-signed identity or exact runtime window attestation. Phase3 lacks newer request capture.'}
dest.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
