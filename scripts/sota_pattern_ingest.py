"""P5 transformations of author-released DOMAINS value occurrences, not semantic errors."""
import hashlib,json,random,time
from pathlib import Path
import numpy as np
import pandas as pd
from tab_err.error_mechanism import ECAR,EAR,ENAR
from thesis_pilot.data import ROOT
from sota_followup.pattern_adapter import BoundedPatternWorker
from sota_followup.benchmarks import AutoTestPattern,statistical_flags
from sota_followup.value_metrics import evaluate_values
O=ROOT/'results/sota_followup/pattern_ingest';O.mkdir(parents=True,exist_ok=True);local=ROOT/'data/sota_followup/pattern_ingest';local.mkdir(parents=True,exist_ok=True)
workers={m:BoundedPatternWorker(m) for m in ['riolu_original','lucario_transductive']};auto=AutoTestPattern('rt_train');inventories=[]
try:
 for dataset in ['dates','ipv4','codes']:
    p=ROOT/f'data/sources/RIOLU/test_data_profiling/homo/{dataset}.json';raw=json.loads(p.read_text());data=list(map(str,raw['Data']));positions=sorted(range(len(data)),key=lambda i:hashlib.sha256(f'{dataset}:{i}'.encode()).hexdigest())[:800];source=pd.DataFrame({'value':[data[i] for i in positions],'source_position':positions},index=[f'{dataset}:{i}' for i in positions]);base=source.value.tolist()
    inventories.append({'dataset':dataset,'source_url':raw['Source'],'source_file_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'original_occurrences':len(data),'scored_occurrences':len(source),'source_positions':positions,'unit':'actual source value occurrence; duplicates retained, no independent population claim'})
    originals={'R':np.zeros(len(source),bool),'RS':statistical_flags(base)}
    for m,w in workers.items():
        try:originals[m]=w.score(base)['flags']
        except Exception:originals[m]=[None]*len(base)
    originals['AutoTest_pattern_only']=auto.score_columns([{'position':0,'header':dataset,'values':base}])[0][0].tolist()
    for mechanism in ['ECAR','EAR','ENAR']:
     for rate in [.01,.05,.1]:
      for seed in [101,202,303,404,505]:
       sid=f'{dataset}_P5_{mechanism}_{int(rate*100)}_{seed}';dest=O/(sid+'.json')
       if dest.exists():continue
       kwargs={'seed':seed}
       if mechanism=='EAR':kwargs['condition_to_column']='source_position'
       state=random.getstate()
       try:mask={'ECAR':ECAR,'EAR':EAR,'ENAR':ENAR}[mechanism](**kwargs).sample(source,'value',rate)
       finally:random.setstate(state)
       dirty=source.copy();logs=[]
       for rid in mask.index[mask.value]:
        value=source.at[rid,'value'];idx=next((i for i,c in enumerate(value) if c in '/-.'),None)
        if dataset=='codes':idx=next((i for i,c in enumerate(value) if c.isdigit()),idx)
        new=value[:idx]+('O' if dataset=='codes' else '_')+value[idx+1:] if idx is not None else value+'@'
        assert new!=value;dirty.at[rid,'value']=new;logs.append({'row_id':rid,'original':value,'new':new,'character_position':idx})
       truth=(source.value!=dirty.value).to_numpy();assert truth.sum()==int(len(source)*rate)
       vals=dirty.value.tolist();flags={'R':np.zeros(len(vals),bool),'RS':statistical_flags(vals)};statuses={}
       for m,w in workers.items():
        try:r=w.score(vals);flags[m]=r['flags'];statuses[m]={k:v for k,v in r.items() if k!='flags'}
        except Exception as error:flags[m]=[None]*len(vals);statuses[m]={'status':'BLOCKED_SOFTWARE','error':repr(error)}
       f,s=auto.score_columns([{'position':0,'header':dataset,'values':vals}]);flags['AutoTest_pattern_only']=f[0].tolist();lp=local/(sid+'.json');lp.write_text(json.dumps(logs));npz=O/(sid+'.npz');np.savez_compressed(npz,truth=truth,**{m:np.array([np.nan if v is None else float(v) for v in f]) for m,f in flags.items()})
       metrics=evaluate_values(flags,truth,np.zeros(len(vals),bool),list(source.index),capacities=(8,20,40))
       for row in metrics:
        method=row['method'];prior=originals[method];current=flags[method];row['newly_triggered_reference_hits']=sum(bool(t) and not bool(old) and bool(new) for t,old,new in zip(truth,prior,current)) if all(v is not None for v in prior) and all(v is not None for v in current) else None
       record={'scenario':sid,'dataset':dataset,'family':'P5_patterned_lexical_transfer','mechanism':mechanism,'rate':rate,'seed':seed,'changed_occurrences':len(logs),'rows':len(source),'truth_category':'B_SOURCE_RELATIVE_INGEST_ALTERATION','original_semantic_correctness':'UNKNOWN','EAR_condition':'immutable observed position in published list; auxiliary ingest-order variable, no invented relational field','prediction_sha256':hashlib.sha256(npz.read_bytes()).hexdigest(),'local_log':str(lp.relative_to(ROOT)),'log_sha256':hashlib.sha256(lp.read_bytes()).hexdigest(),'statuses':statuses,'metrics':metrics};dest.write_text(json.dumps(record,separators=(',',':')))
    print(dataset,'45 P5 cases complete',flush=True)
finally:
 for w in workers.values():w.close()
(ROOT/'manifests/sota_followup/pattern_sources.json').write_text(json.dumps(inventories,indent=2)+'\n')
