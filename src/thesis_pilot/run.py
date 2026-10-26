import argparse,hashlib,json,time,traceback,os,platform,resource
from pathlib import Path
import numpy as np
import pandas as pd
from .data import ROOT,SPECS,load,contracts,shash
from .controls import Controls
from .inject import scenarios,inject
from .models import Native,ContextualTrees
from .evaluate import evaluate_all

def methods():
 return [Native('dboost_text_original',ROOT/'data/sources/cpitclaudel__dBoost',ROOT/'data/envs/pilot/bin/python'),Native('dboost_numeric_original',ROOT/'data/sources/cpitclaudel__dBoost',ROOT/'data/envs/pilot/bin/python'),Native('lucario_original_history',ROOT/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO',ROOT/'data/envs/lucario/bin/python'),ContextualTrees(),Native('cdc_original',Path('/workspace/research_sources/se-jaeger__conformal-data-cleaning'),ROOT/'data/envs/cdc/bin/python')]

def run_dataset(name,smoke=False,selected=None):
 out=ROOT/'results/thesis_pilot';art=out/'predictions';art.mkdir(parents=True,exist_ok=True);raw=ROOT/'data/pilot_runs';raw.mkdir(exist_ok=True)
 parts,meta=load(name);spec=SPECS[name];targets=spec['targets'];history=parts['history'][targets];batch=parts['evaluation'][targets];cat=[c for c in spec['categorical'] if c in targets];contract=contracts(name,parts['history']);rules=Controls(contract,targets,cat).fit(history)
 (out/(name+'_population.json')).write_text(json.dumps(meta,indent=2));(out/(name+'_contracts.json')).write_text(json.dumps({'contract':contract,'statistical_provenance':rules.provenance,'fit_scope':'history only','key_referential_reconciliation':'NOT_APPLICABLE in this single-table cell track; separate explicit fixture'},indent=2))
 fitted=[];status=[];original={};original['A'],original['B']=rules.score(batch)
 for model in methods():
  if selected and model.name not in selected:continue
  t=time.perf_counter()
  try:
   if isinstance(model,Native):model.fit(history,targets,cat,name)
   else:model.fit(history,targets,cat)
   original[model.name]=model.score(batch);fitted.append(model)
   status.append({'method':model.name,'status':'EXECUTED_CONDITIONAL','fit_seconds':time.perf_counter()-t,'untouched_alerts':int(original[model.name].sum())})
   print(name,'fitted',model.name,round(time.perf_counter()-t,2),'seconds',flush=True)
  except Exception as e:
   status.append({'method':model.name,'status':'BLOCKED_TECHNICAL','error':repr(e),'fit_seconds':time.perf_counter()-t});model.close();print(name,'FIT FAILURE',model.name,repr(e),flush=True)
 (out/(name+'_method_status.json')).write_text(json.dumps(status,indent=2));np.savez_compressed(art/(name+'_untouched.npz'),**original)
 protocol=json.loads((ROOT/'configs/thesis_pilot/protocol_v1.json').read_text());proto_hash=shash(ROOT/'configs/thesis_pilot/protocol_v1.json')
 all_cases=scenarios(name);seeds=protocol['seeds'];rates=protocol['rates']
 if smoke:seeds=seeds[:1];rates=[.05]
 count=0
 try:
  for case in all_cases:
   for mechanism in protocol['mechanisms']:
    for rate in rates:
     for seed in seeds:
      sid=f'{name}_{case[0]}_{mechanism}_{int(rate*100)}_{seed}';npz=art/(sid+'.npz');result=out/'scenarios'/(sid+'.json');result.parent.mkdir(exist_ok=True)
      # Only reuse exact protocol and implementation fingerprint matches.
      codehash=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT/'src/thesis_pilot').glob('*.py')))+(ROOT/'scripts/native_detector_worker.py').read_bytes()).hexdigest()
      if result.exists():
       prior=json.loads(result.read_text())
       if prior.get('protocol_sha256')==proto_hash and prior.get('code_sha256')==codehash:count+=1;continue
       raise RuntimeError('Existing checkpoint invalidated; choose versioned results directory rather than overwrite: '+sid)
      t=time.perf_counter();changed,logs,diagnostics=inject(batch,name,case,mechanism,rate,seed);truth=np.zeros((len(batch),len(targets)),bool)
      for entry in logs:truth[batch.index.get_loc(entry['source_row_id']),targets.index(entry['column'])]=True
      a,b=rules.score(changed);preds={'A':a,'B':b};failures=[];times={}
      for model in fitted:
       start=time.perf_counter()
       # Explicit domain exclusions avoid rows disappearing in native parsers.
       numeric_invalid=any(pd.to_numeric(changed[c],errors='coerce').isna().any() for c in targets if c not in cat)
       if numeric_invalid and model.name in {'dboost_numeric_original','cdc_original'}:
        failures.append({'method':model.name,'status':'INCOMPATIBLE_SCENARIO','reason':'Non-numeric/missing intervention outside native numeric input support; no dropped rows or zero-score replacement'});continue
       try:preds[model.name]=model.score(changed)
       except Exception as e:failures.append({'method':model.name,'status':'BLOCKED_TECHNICAL','reason':repr(e)})
       times[model.name]=time.perf_counter()-start
      np.savez_compressed(npz,truth=truth,**preds)
      logpath=raw/(sid+'.json');logpath.write_text(json.dumps(logs,indent=2))
      recordmeta={'scenario':sid,'dataset':name,'family':case[0],'mechanism':mechanism,'rate':rate,'seed':seed,'target':case[1],'label_status':case[3]}
      metrics=evaluate_all(preds,original,truth,list(batch.index),targets,recordmeta)
      saved={**recordmeta,'protocol_sha256':proto_hash,'code_sha256':codehash,'diagnostics':diagnostics,'predictions_sha256':shash(npz),'injection_log_sha256':shash(logpath),'injection_log':str(logpath.relative_to(ROOT)),'timing':times,'failures':failures,'seconds':time.perf_counter()-t,'metrics':metrics}
      result.write_text(json.dumps(saved,indent=2));count+=1
      if count%15==0:print(name,count,'scenarios completed',round(saved['seconds'],2),'sec latest',flush=True)
 finally:
  for m in fitted:m.close()
 print(name,'COMPLETED',count,flush=True)
 return count

def main():
 p=argparse.ArgumentParser();p.add_argument('--datasets',nargs='+',default=['credit','bank','wine']);p.add_argument('--smoke',action='store_true');p.add_argument('--methods',nargs='*');args=p.parse_args()
 for name in args.datasets:run_dataset(name,args.smoke,args.methods)
if __name__=='__main__':main()
