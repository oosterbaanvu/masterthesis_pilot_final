"""Targeted post hoc dtype repair test; original results remain the primary record."""
import json,os,subprocess,time
import numpy as np
from thesis_pilot.data import ROOT,SPECS,load,contracts
from thesis_pilot.controls import Controls
from thesis_pilot.models import Native
from thesis_pilot.inject import scenarios,inject
from thesis_pilot.evaluate import evaluate_all

class DeclaredCDC(Native):
 def __init__(self):super().__init__('cdc_source_type_adaptation','/workspace/research_sources/se-jaeger__conformal-data-cleaning',ROOT/'data/envs/cdc/bin/python')
 def fit(self,df,targets,cat,dataset):
  self.columns=list(df);self.targets=targets;self.log=(ROOT/'evidence/thesis_pilot'/(dataset+'_cdc_source_types.log')).open('w')
  self.proc=subprocess.Popen([self.python,str(ROOT/'scripts/cdc_source_type_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',PYTHONHASHSEED='0'))
  meta=self.call({'op':'fit','method':'cdc_original','source':self.source,'rows':df.values.tolist(),'columns':self.columns,'targets':targets,'categorical':cat,'model_path':str(ROOT/'data/pilot_models'/dataset/self.name)},timeout=420)
  (ROOT/'evidence/thesis_pilot'/(dataset+'_cdc_source_types_fit.json')).write_text(json.dumps(meta,indent=2));return self

out=ROOT/'results/thesis_pilot/cdc_type_diagnostic';out.mkdir(exist_ok=True);records=[]
for name in ['credit','bank','wine']:
 parts,pop=load(name);s=SPECS[name];h=parts['history'];batch=parts['evaluation'];targets=s['targets'];rules=Controls(contracts(name,h),targets,s['categorical']).fit(h)
 originals={};originals['A'],originals['B']=rules.score(batch);m=DeclaredCDC();start=time.perf_counter()
 try:
  m.fit(h,targets,s['categorical'],name+'_source_type_diagnostic');originals[m.name]=m.score(batch)
  untouched={'dataset':name,'source_feature_count':len(h.columns),'untouched_alerts':int(originals[m.name].sum()),'A_untouched_alerts':int(originals['A'].sum()),'B_untouched_alerts':int(originals['B'].sum()),'method':'cdc_source_type_adaptation','fit_and_untouched_seconds':time.perf_counter()-start}
  np.savez_compressed(out/(name+'_untouched.npz'),**originals)
  for case in scenarios(name):
   if case[0] not in ['E4_scale','E5_substitution']:continue
   for mechanism in ['ECAR','EAR','ENAR']:
    changed,logs,diag=inject(batch,name,case,mechanism,.05,101);truth=np.zeros((len(batch),4),bool)
    for e in logs:truth[batch.index.get_loc(e['source_row_id']),targets.index(e['column'])]=True
    preds={};preds['A'],preds['B']=rules.score(changed);preds[m.name]=m.score(changed);sid=f'{name}_{case[0]}_{mechanism}'
    np.savez_compressed(out/(sid+'.npz'),truth=truth,**preds)
    meta={'scenario':sid,'dataset':name,'family':case[0],'mechanism':mechanism,'rate':.05,'seed':101,'target':case[1],'label_status':case[3],'scope':'post hoc source-type repair, all input features, same frozen source split; no new thresholds or choice of best test configuration'}
    metrics=evaluate_all(preds,originals,truth,list(batch.index),targets,meta);records.append({**meta,'untouched':untouched,'metrics':metrics})
  print(name,untouched,flush=True)
 finally:m.close()
(out/'results.json').write_text(json.dumps(records,indent=2));print('18 source-type diagnostic scenarios executed; primary native-dtype evidence preserved')
