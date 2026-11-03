#!/usr/bin/env python3
"""Run unchanged capsule audit logic in a disposable copy; never start a server.
Usage: python replay_offline.py /absolute/disposable/output
Network and provider construction fail closed; original manifest checked before/after.
"""
import hashlib, importlib.metadata, json, lzma, os, pathlib, platform, resource, shutil, socket, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[3]
OUT=pathlib.Path(sys.argv[1]).resolve()
assert not OUT.exists(), 'output must not exist'
assert ROOT not in OUT.parents, 'disposable output must be outside source clone'
OUT.mkdir(parents=True)
CAP=OUT/'capsule'; shutil.copytree(ROOT/'capsule',CAP)
def check_manifest():
    rows=[]
    for line in (CAP/'SHA256SUMS.capsule').read_text().splitlines():
        sha,name=line.split(None,1); name=name.lstrip('* ')
        actual=hashlib.sha256((CAP/name).read_bytes()).hexdigest()
        assert actual==sha, f'capsule manifest mismatch: {name}'
        rows.append(name)
    return len(rows)
manifest_files=check_manifest()
for name in ('engine.db','budget.db'):
    target=CAP/'artifacts/api-server/engine/data'/name;target.parent.mkdir(parents=True,exist_ok=True)
    with lzma.open(CAP/'data'/f'{name}.xz','rb') as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
for name in ('phase4-driver-plan.json','phase4-driver-state.json','phase5-driver-plan.json','phase5-driver-state.json'):
    shutil.copy2(CAP/'data'/name,CAP/'artifacts/api-server/engine/data'/name)
# No credential values are read: remove variable names before engine imports.
for key in list(os.environ):
    if any(s in key.upper() for s in ('API_KEY','TOKEN','SECRET','AI_INTEGRATIONS','PASSWORD','CREDENTIAL')):del os.environ[key]
attempts=[]
def deny(*args,**kwargs):
    attempts.append('network-or-provider');raise RuntimeError('offline replay forbids network/provider construction')
socket.socket.connect=deny;socket.socket.connect_ex=deny;socket.create_connection=deny;socket.socket.bind=deny
sys.path.insert(0,str(CAP/'artifacts/api-server/engine'))
import llm_subject, llm_runner, phase4_runner, phase5_runner
for mod in (llm_subject,llm_runner,phase4_runner,phase5_runner):
    if hasattr(mod,'make_provider'):mod.make_provider=deny
from engine import Engine
from phase4 import ArmStore
import phase3_replay_audit as p3,phase4_step8_audit as p4,phase5_replay_audit as p5
start=time.monotonic()
assert p3.main()==0
# Only transport changes: same phase4 replay function behind the HTTP endpoint,
# same audit population, RNG profile checks and default checksum manifest.
e=Engine(str(CAP/'artifacts/api-server/engine/data/engine.db'));store=ArmStore()
p4._replay=lambda rid:phase4_runner.replay_llm_p4(e,rid,store=store)
p4.ENGINE='in-process:no-network';os.environ['STEP8_PHASE4_ONLY']='1'
assert p4.main()==0
assert p5.main()==0
reports={
 'phase3':CAP/'docs/analysis/submission/v12/phase3-replay-audit.json',
 'phase4':CAP/'docs/phase4/step8-replay-audit.json',
 'phase5':CAP/'docs/phase5-close/replay-audit.json'}
# Audit reports carry current timestamps; restore ONLY reports from source before
# rechecking original manifest, exactly the original transactional shell contract.
summary={k:json.loads(v.read_text()) for k,v in reports.items()}
for k,v in reports.items():shutil.copy2(v,OUT/f'{k}-replay-audit.json')
for rel in ('docs/analysis/submission/v12/phase3-replay-audit','docs/phase4/step8-replay-audit','docs/phase5-close/replay-audit'):
    for ext in ('json','md'):shutil.copy2(ROOT/'capsule'/f'{rel}.{ext}',CAP/f'{rel}.{ext}')
assert check_manifest()==manifest_files
assert not attempts
# Derive identities from native audit reports; fail closed on scope drift.
t3=summary['phase3']['totals'];t4=summary['phase4']['totals'];t5=summary['phase5']['totals']
registered=summary['phase3']['registeredLlmRuns'];legacy=summary['phase3']['additionalLegacyLlmRuns']
assert registered==sum(summary['phase3']['expectedPromptCounts'].values())==320
assert legacy==3 and t3['llmRuns']==registered+legacy==t3['llmRunsOk']==323
assert t3['baselineRuns']==t3['baselineRunsOk']==20
assert t4['runs']==2888 and t4['replayedObservations']==2864 and t4['partialsSkippedBySignature']==24
assert t4['runs']==t4['replayedObservations']+t4['invalidTrialsVerified']+t4['partialsSkippedBySignature']
assert t5['runs']==t5['ok']==1712 and t5['invalidTrials']==0
llm_total=t3['llmRuns']+t4['replayedObservations']+t5['runs']
all_total=llm_total+t3['baselineRuns'];confirmatory=all_total-legacy
assert (llm_total,all_total,confirmatory)==(4899,4919,4916)
counts={'confirmatory_runs':confirmatory,'legacy_diagnostic_runs':legacy,'total_verifier_runs':all_total,'confirmatory_llm_runs':llm_total-legacy,'verifier_llm_runs_including_legacy':llm_total,'deterministic_baselines':t3['baselineRuns']}
receipt={'source_base':'62ab90beff1d291b069c87f13b6b6b3495171ddd','route':'native audit logic, phase4 in-process transport adapter; not unmodified verify.sh','manifest_sha256':hashlib.sha256((CAP/'SHA256SUMS.capsule').read_bytes()).hexdigest(),'manifest_files_checked_before_and_after':manifest_files,'network_attempts':len(attempts),'listening_ports':0,'provider_construction':0,'elapsed_seconds':round(time.monotonic()-start,2),'max_rss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'python':sys.version,'platform':platform.platform(),'dependencies':{n:importlib.metadata.version(n) for n in ('activegraph','numpy','scipy','pydantic')},'counts':counts,'reports':{k:v['totals'] for k,v in summary.items()},'verdict':'PASS'}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
