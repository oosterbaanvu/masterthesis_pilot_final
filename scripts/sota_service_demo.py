"""Synthetic public-pattern fixture; source registration and scan, no oracle in adapter."""
import hashlib,json,os,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data/sota_followup/service';D.mkdir(parents=True,exist_ok=True);source=D/'source.csv';contract=D/'contract.json'
# Simple invoice code is intentionally easy: interface validation, not a research win.
values=[f'INV-{i:06d}' for i in range(400)]
for i in range(0,400,40):values[i]='?'*7
source.write_text('invoice_code\n'+'\n'.join(values)+'\n');contract.write_text(json.dumps({'columns':{'invoice_code':{'type':'text','required':True,'provenance':'EXPLICIT_STIPULATED_CONTRACT'}},'targets':['invoice_code']}));before=hashlib.sha256(source.read_bytes()).hexdigest();py=R/'data/envs/sota/bin/python';env=dict(os.environ,PYTHONPATH=str(R/'src'),PYTHONHASHSEED='0')
subprocess.run([str(py),'-m','dq_service','register','--id','sota_pattern_demo','--csv',str(source),'--contract',str(contract)],cwd=R,env=env,check=True)
for method in ['riolu_original','riolu_small_sample','lucario_transductive','autotest_pattern_only']:
 dest=R/'results/sota_followup/service_demo'/method;subprocess.run([str(py),'-m','dq_service','pattern-scan','--id','sota_pattern_demo','--detector',method,'--output',str(dest)],cwd=R,env=env,check=True);d=json.loads((dest/'report.json').read_text());assert d['source_unchanged'] and d['eligible_columns']==1 and d['alerts']==10
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
print('Four actual CLI adapters returned10 suspicious coordinates each; original file unchanged')
