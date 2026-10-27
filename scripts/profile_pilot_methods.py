"""Representative process footprint at the frozen Credit workload; not benchmark-wide peak claims."""
import json,os,resource,time
from thesis_pilot.data import ROOT,load,SPECS
from thesis_pilot.models import Native,ContextualTrees
parts,_=load('credit');s=SPECS['credit'];h=parts['history'][s['targets']];b=parts['evaluation'][s['targets']];cat=[c for c in s['categorical'] if c in s['targets']]
items=[Native('dboost_text_original',ROOT/'data/sources/cpitclaudel__dBoost',ROOT/'data/envs/pilot/bin/python'),Native('dboost_numeric_original',ROOT/'data/sources/cpitclaudel__dBoost',ROOT/'data/envs/pilot/bin/python'),Native('lucario_original_history',ROOT/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO',ROOT/'data/envs/lucario/bin/python'),ContextualTrees(),Native('cdc_original','/workspace/research_sources/se-jaeger__conformal-data-cleaning',ROOT/'data/envs/cdc/bin/python')]
rows=[]
for m in items:
 t=time.perf_counter()
 try:
  if isinstance(m,Native):m.fit(h,s['targets'],cat,'profile_credit')
  else:m.fit(h,s['targets'],cat)
  fitted=time.perf_counter()-t;start=time.perf_counter();f=m.score(b);scored=time.perf_counter()-start
  if isinstance(m,Native):
   text=open(f'/proc/{m.proc.pid}/status').read();rss=next(int(line.split()[1]) for line in text.splitlines() if line.startswith('VmHWM:'));scope='worker high-water RSS after fit and untouched score; parent and descendants not summed'
  else:rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss;scope='parent high-water RSS includes other already imported libraries; not isolated algorithm allocation'
  rows.append({'method':m.name,'status':'EXECUTED_CONDITIONAL','history_rows':len(h),'batch_rows':len(b),'input_columns':4,'fit_seconds':fitted,'score_seconds':scored,'rss_high_water_kib':rss,'memory_scope':scope,'alerts':int(f.sum())})
 except Exception as e:rows.append({'method':m.name,'status':'BLOCKED_TECHNICAL','error':repr(e)})
 finally:m.close()
(ROOT/'evidence/thesis_pilot/method_resource_profile.json').write_text(json.dumps(rows,indent=2));print(rows)
