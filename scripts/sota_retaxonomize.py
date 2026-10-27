"""New analysis of cached historical flags; not new detector executions."""
import gzip,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd
from thesis_pilot.data import ROOT,SPECS,load,contracts
from sota_followup.layers import Layers
from sota_followup.metrics import evaluate

out=ROOT/'results/sota_followup/historical_retaxonomy';out.mkdir(parents=True,exist_ok=True);records=[];counts={}
for name in ['credit','bank','wine']:
    parts,_=load(name);spec=SPECS[name];targets=spec['targets'];history=parts['history'][targets];source=parts['evaluation'][targets];rules=Layers(contracts(name,parts['history']),targets,[c for c in spec['categorical'] if c in targets]).fit(history)
    old=np.load(ROOT/f'results/thesis_pilot/predictions/{name}_untouched.npz');untouched=rules.score_layers(source)
    assert np.array_equal(untouched['R'],old['A']) and np.array_equal(untouched['RSM'],old['B'])
    untouched.update({k:old[k] for k in old.files if k not in ['A','B']});count=0
    for path in sorted((ROOT/'results/thesis_pilot/scenarios').glob(name+'_*.json')):
        d=json.loads(path.read_text());batch=source.copy();lp=ROOT/d['injection_log']
        if not lp.exists():
            from thesis_pilot.inject import scenarios,inject
            case=next(c for c in scenarios(name) if c[0]==d['family']);_,logs,_=inject(source,name,case,d['mechanism'],d['rate'],d['seed']);raw=json.dumps(logs,indent=2).encode();assert hashlib.sha256(raw).hexdigest()==d['injection_log_sha256'];lp.parent.mkdir(parents=True,exist_ok=True);lp.write_bytes(raw)
        logs=json.loads(lp.read_text())
        for entry in logs:batch.at[entry['source_row_id'],entry['column']]=entry['new']
        z=np.load(ROOT/'results/thesis_pilot/predictions'/(d['scenario']+'.npz'));layers=rules.score_layers(batch)
        assert np.array_equal(layers['R'],z['A']) and np.array_equal(layers['RSM'],z['B'])
        preds={**layers,**{k:z[k] for k in z.files if k not in ['A','B','truth']}}
        np.savez_compressed(out/(d['scenario']+'_layers.npz'),**layers)
        meta={k:d[k] for k in ['scenario','dataset','family','mechanism','rate','seed','label_status']}
        for row in evaluate(preds,untouched,z['truth'],list(source.index),targets):records.append({**meta,**row})
        count+=1
    counts[name]=count;print(name,count,'cached cases retaxonomized; no detector refit',flush=True)
pd.DataFrame(records).to_csv(out/'metrics.csv.gz',index=False,compression={'method':'gzip','mtime':0})
(out/'manifest.json').write_text(json.dumps({'status':'EXECUTED_POSTHOC_ANALYSIS','historical_cases':counts,'metric_rows':len(records),'old_A_equals_R_and_old_B_equals_RSM':True,'new_detector_executions':0,'new_layer':'RS exposes the original univariate profile without Ridge','historical_results_preserved':True},indent=2)+'\n')
