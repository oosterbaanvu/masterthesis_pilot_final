"""Recover ignored source-value transformation logs from frozen deterministic operations."""
import hashlib,json,random
from pathlib import Path
import pandas as pd
from thesis_pilot.data import ROOT,load
from sota_followup.interventions import CASES,alter
from tab_err.error_mechanism import ECAR,EAR,ENAR
O=ROOT/'results/sota_followup';parts={}
for p in sorted((O/'ingest').glob('*.json')):
 d=json.loads(p.read_text())
 if 'scenario' not in d:continue
 target=ROOT/d['log_path']
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==d['log_sha256'];continue
 name=d['dataset']
 if name not in parts:parts[name]=load(name)[0]
 case=next(c for c in CASES[name] if c[0]==d['family']);_,logs,_=alter(parts[name]['evaluation'],case,d['mechanism'],d['rate'],d['seed'],d['diagnostics']['condition']);raw=json.dumps(logs).encode();assert hashlib.sha256(raw).hexdigest()==d['log_sha256'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
for p in sorted((O/'pattern_ingest').glob('*.json')):
 d=json.loads(p.read_text());target=ROOT/d['local_log']
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==d['log_sha256'];continue
 s=next(v for v in json.loads((ROOT/'manifests/sota_followup/pattern_sources.json').read_text()) if v['dataset']==d['dataset']);raw=json.loads((ROOT/f"data/sources/RIOLU/test_data_profiling/homo/{d['dataset']}.json").read_text())['Data'];positions=s['source_positions'];source=pd.DataFrame({'value':[str(raw[i]) for i in positions],'source_position':positions},index=[f"{d['dataset']}:{i}" for i in positions]);kwargs={'seed':d['seed']}
 if d['mechanism']=='EAR':kwargs['condition_to_column']='source_position'
 state=random.getstate()
 try:mask={'ECAR':ECAR,'EAR':EAR,'ENAR':ENAR}[d['mechanism']](**kwargs).sample(source,'value',d['rate'])
 finally:random.setstate(state)
 logs=[]
 for rid in mask.index[mask.value]:
  value=source.at[rid,'value'];idx=next((i for i,c in enumerate(value) if c in '/-.'),None)
  if d['dataset']=='codes':idx=next((i for i,c in enumerate(value) if c.isdigit()),idx)
  new=value[:idx]+('O' if d['dataset']=='codes' else '_')+value[idx+1:] if idx is not None else value+'@';logs.append({'row_id':rid,'original':value,'new':new,'character_position':idx})
 raw=json.dumps(logs).encode();assert hashlib.sha256(raw).hexdigest()==d['log_sha256'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
print('All855 context/occurrence transformation logs verified or exactly restored')
