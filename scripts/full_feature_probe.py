"""Post-smoke, explicitly exploratory information-scope sensitivity.
Same frozen split, targets, 5% transformations and settings; extra original source
features supplied to both the extended linear baseline and contextual methods.
Not pooled into the predeclared 630-scenario primary grid.
"""
import json,time,traceback
import numpy as np
from thesis_pilot.data import ROOT,SPECS,load,contracts
from thesis_pilot.controls import Controls
from thesis_pilot.models import ContextualTrees,Native
from thesis_pilot.inject import scenarios,inject
from thesis_pilot.evaluate import evaluate_all
out=ROOT/'results/thesis_pilot/full_feature_probe';out.mkdir(exist_ok=True);records=[]
for name in ['credit','bank','wine']:
 parts,pop=load(name);s=SPECS[name];h=parts['history'];batch=parts['evaluation'];targets=s['targets'];rules=Controls(contracts(name,h),targets,s['categorical']).fit(h)
 original={};original['A'],original['B']=rules.score(batch);models=[];statuses=[]
 candidates=[ContextualTrees(),Native('cdc_original','/workspace/research_sources/se-jaeger__conformal-data-cleaning',ROOT/'data/envs/cdc/bin/python')]
 try:
  for m in candidates:
   try:
    if isinstance(m,Native):m.fit(h,targets,s['categorical'],name+'_full_feature_probe')
    else:m.fit(h,targets,s['categorical'])
    original[m.name]=m.score(batch);models.append(m);statuses.append({'method':m.name,'status':'EXECUTED_CONDITIONAL'})
   except Exception as e:statuses.append({'method':m.name,'status':'BLOCKED_TECHNICAL','reason':repr(e)});m.close()
  for case in scenarios(name):
   if case[0] not in ['E4_scale','E5_substitution']:continue
   for mechanism in ['ECAR','EAR','ENAR']:
    changed,logs,diag=inject(batch,name,case,mechanism,.05,101);truth=np.zeros((len(batch),4),bool)
    for e in logs:truth[batch.index.get_loc(e['source_row_id']),targets.index(e['column'])]=True
    preds={};preds['A'],preds['B']=rules.score(changed)
    for m in models:preds[m.name]=m.score(changed)
    sid=f'{name}_{case[0]}_{mechanism}';np.savez_compressed(out/(sid+'.npz'),truth=truth,**preds)
    meta={'scenario':sid,'dataset':name,'family':case[0],'mechanism':mechanism,'rate':.05,'seed':101,'target':case[1],'label_status':case[3],'feature_count':len(batch.columns),'evaluated_columns':targets,'regime':'all original non-outcome feature columns; source-disjointness unchanged; exploratory scope sensitivity'}
    metric=evaluate_all(preds,original,truth,list(batch.index),targets,meta);records.append({**meta,'diagnostics':diag,'methods':statuses,'metrics':metric})
  print(name,'full-feature sensitivity complete',len(batch.columns),'input columns',flush=True)
 finally:
  for m in models:m.close()
(out/'results.json').write_text(json.dumps(records,indent=2));print('Completed',len(records),'source/family/mechanism scope probes')
