"""Publisher-reference track; never pooled with injection or independent semantic labels."""
import json,time
from pathlib import Path
import numpy as np
import pandas as pd
from thesis_pilot.data import ROOT
from thesis_pilot.models import Native
from thesis_pilot.evaluate import ordering,schedule

def run(name):
 base=ROOT/'data/raw/BigDaMa__raha/datasets'/name
 dirty=pd.read_csv(base/'dirty.csv',dtype=str,keep_default_na=False);clean=pd.read_csv(base/'clean.csv',dtype=str,keep_default_na=False)
 assert dirty.shape==clean.shape
 # Pin explicit source schema maps; do not guess column correspondence.
 maps=json.loads((ROOT/'configs/schema_maps.json').read_text());key='raha_'+name
 if list(clean)!=list(dirty):
  assert maps[key]['dirty']==list(dirty) and maps[key]['reference']==list(clean);clean.columns=dirty.columns
 drop=[c for c in ['index','id'] if c in dirty];dirty=dirty.drop(columns=drop);clean=clean.drop(columns=drop);targets=list(dirty)
 truth=dirty.to_numpy()!=clean.to_numpy()
 # A: lexical-only conventional screen; empty conventions are explicit heuristics, not universal requiredness.
 a=dirty.isin(['','empty','NULL','N/A']).to_numpy();b=a.copy()
 for j,c in enumerate(targets):
  if c in ['provider_number','zip','phone','brewery_id']:continue
  numeric=pd.to_numeric(dirty[c],errors='coerce')
  if numeric.notna().mean()>.95:
   lo,hi=numeric.quantile([.005,.995]);b[:,j]|=((numeric<lo)|(numeric>hi)).to_numpy()
  elif dirty[c].nunique()<len(dirty)*.5:
   share=dirty[c].map(dirty[c].value_counts(normalize=True));b[:,j]|=(share<.005).to_numpy()
 preds={'A':a,'B':b};status=[]
 source_l=ROOT/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO';source_d=ROOT/'data/sources/cpitclaudel__dBoost'
 # Same unlabeled current table for fit, explicit transductive regime. No clean table supplied to a detector.
 for method,source,py in [('lucario_original_history',source_l,ROOT/'data/envs/lucario/bin/python'),('dboost_text_original',source_d,ROOT/'data/envs/pilot/bin/python')]:
  m=Native(method,source,py);start=time.perf_counter()
  try:m.fit(dirty,targets,targets,'external_'+name);preds[method]=m.score(dirty);status.append({'method':method,'state':'EXECUTED_CONDITIONAL','seconds':time.perf_counter()-start})
  except Exception as e:status.append({'method':method,'state':'BLOCKED_TECHNICAL','error':repr(e)})
  finally:m.close()
 out=ROOT/'results/thesis_pilot/external';out.mkdir(exist_ok=True)
 np.savez_compressed(out/(name+'.npz'),truth=truth,**preds)
 results=[]
 for baseline in ['A','B']:
  for method,flag in preds.items():
   if method in ['A','B'] and method!=baseline:continue
   union=preds[baseline]|flag;extra=flag&~preds[baseline]
   results.append({'baseline':baseline,'method':method,'reference_hits':int((flag&truth).sum()),'alerts':int(flag.sum()),'union_reference_hits':int((union&truth).sum()),'additional_reference_hits':int((extra&truth).sum()),'additional_alerts':int(extra.sum()),'marginal_reference_precision':float((extra&truth).sum()/extra.sum()) if extra.any() else None})
 meta={'dataset':name,'shape':list(dirty.shape),'published_raw_disagreements':int(truth.sum()),'unit':'cell','fit_scope':'unlabelled current batch, transductive','reference_semantics':'raw publisher-reference disagreements; uncertain and representation changes retained as reference targets, NOT independently verified semantic errors','baseline_status':'generic lexical/statistical heuristics; not a mature domain-specific enterprise suite','outcomes':results,'method_status':status,'source_ids_excluded':drop,'classifier_history_used':False}
 (out/(name+'.json')).write_text(json.dumps(meta,indent=2));print(name,meta['published_raw_disagreements'],status,flush=True)
for name in ['hospital','beers']:run(name)
