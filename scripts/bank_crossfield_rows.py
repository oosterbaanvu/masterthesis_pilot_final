"""Separate documented/stipulated row-level cross-field experiment; no invented cell blame."""
import json,random,time
import numpy as np
import pandas as pd
from tab_err.error_mechanism import ECAR,EAR,ENAR
from thesis_pilot.data import ROOT,load,SPECS,contracts
from thesis_pilot.controls import Controls
from thesis_pilot.models import Native,ContextualTrees
from thesis_pilot.evaluate import evaluate_all
out=ROOT/'results/thesis_pilot/bank_crossfield_rows';out.mkdir(exist_ok=True);parts,pop=load('bank');h=parts['history'];batch=parts['evaluation'];s=SPECS['bank'];targets=s['targets']

def relation(df):return (pd.to_numeric(df.previous)==0).to_numpy()!=(df.poutcome.astype(str)=='nonexistent').to_numpy()
assert not relation(h).any() and not relation(batch).any()
rules=Controls(contracts('bank',h),targets,s['categorical']).fit(h);a,b=rules.score(batch);original={'A':a.any(axis=1)[:,None],'B':(b.any(axis=1)|relation(batch))[:,None]}
models=[];statuses=[]
for m in [ContextualTrees(),Native('cdc_original','/workspace/research_sources/se-jaeger__conformal-data-cleaning',ROOT/'data/envs/cdc/bin/python'),Native('lucario_original_history',ROOT/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO',ROOT/'data/envs/lucario/bin/python'),Native('dboost_text_original',ROOT/'data/sources/cpitclaudel__dBoost',ROOT/'data/envs/pilot/bin/python')]:
 try:
  if isinstance(m,Native):m.fit(h,targets,s['categorical'],'bank_crossfield_row')
  else:m.fit(h,targets,s['categorical'])
  original[m.name]=m.score(batch).any(axis=1)[:,None];models.append(m);statuses.append({'method':m.name,'status':'EXECUTED_CONDITIONAL'})
 except Exception as e:statuses.append({'method':m.name,'status':'BLOCKED_TECHNICAL','error':repr(e)});m.close()
np.savez_compressed(out/'untouched.npz',**original)
eligible=(pd.to_numeric(batch.previous)>0)&batch.poutcome.isin(['failure','success']);sub=batch.loc[eligible].copy();sub['previous']=pd.to_numeric(sub.previous);sub['age']=pd.to_numeric(sub.age);assert sub.previous.nunique()>1
records=[]
try:
 for mechanism in ['ECAR','EAR','ENAR']:
  for rate in [.01,.05,.10]:
   for seed in [101,202,303,404,505]:
    n=max(1,int(len(sub)*rate));cls={'ECAR':ECAR,'EAR':EAR,'ENAR':ENAR}[mechanism];args={'seed':seed}
    if mechanism=='EAR':args['condition_to_column']='age'
    state=random.getstate()
    try:mask=cls(**args).sample(sub,'previous',(n+.25)/len(sub))
    finally:random.setstate(state)
    ids=mask.index[mask.previous];x=batch.copy();x.loc[ids,'previous']=0.;assert (x.astype(str)!=batch.astype(str)).to_numpy().sum()==n
    truth=np.array(batch.index.isin(ids),bool)[:,None];require=relation(x);assert np.array_equal(require,truth[:,0])
    a,b=rules.score(x);preds={'A':a.any(axis=1)[:,None],'B':(b.any(axis=1)|require)[:,None]}
    for m in models:preds[m.name]=m.score(x).any(axis=1)[:,None]
    sid=f'E6_bank_{mechanism}_{int(rate*100)}_{seed}';np.savez_compressed(out/(sid+'.npz'),truth=truth,**preds)
    meta={'scenario':sid,'dataset':'bank','family':'E6_crossfield','mechanism':mechanism,'rate':rate,'seed':seed,'target':'row','label_status':'VERIFIED_STIPULATED_ROW_CONTRACT','unit':'row review; never pooled with cell localization','eligible_count':len(sub),'intended_count':n,'realized_count':n,'changed_row_ids':list(ids),'contract':'previous=0 iff poutcome=nonexistent','methods':statuses}
    records.append({**meta,'metrics':evaluate_all(preds,original,truth,list(batch.index),['row'],meta)})
 print('Executed',len(records),'row scenarios; eligible rows',len(sub),flush=True)
finally:
 for m in models:m.close()
(out/'results.json').write_text(json.dumps(records,indent=2))
