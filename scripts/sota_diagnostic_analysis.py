"""Post hoc descriptive severity, counterpart, CDC and review-policy sensitivities."""
import hashlib,itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from thesis_pilot.data import ROOT,load
O=ROOT/'results/sota_followup';magnitudes=[];counter=[];shared={};parts={name:load(name)[0] for name in ['credit','bank','wine']}
for p in sorted((O/'ingest').glob('*.json')):
 d=json.loads(p.read_text())
 if 'scenario' not in d:continue
 z=np.load(p.with_suffix('.npz'));u=np.load(O/f"ingest/{d['dataset']}_{d['view']}_untouched.npz");logs=json.loads((ROOT/d['log_path']).read_text());target=d['diagnostics']['target'];history=parts[d['dataset']]['history'];q=pd.to_numeric(history[target],errors='coerce').quantile([.25,.75]);iqr=q.iloc[1]-q.iloc[0]
 if d['view']=='full':
  for e in logs:
   key=(d['dataset'],d['family'],d['seed'],e['row_id']);new=str(e['new']);assert shared.get(key,new)==new;shared[key]=new
   try:
    before=float(e['original']);after=float(e['new']);absolute=abs(after-before);magnitudes.append({**{k:d[k] for k in ['dataset','family','mechanism','rate','seed']},'absolute':absolute,'relative':absolute/abs(before) if before else None,'history_IQR_normalized':absolute/iqr if iqr else None,'relative_undefined_zero_source':before==0})
   except (ValueError,TypeError):pass
 for baseline in ['R','RS','RSM']:
  for method in ['cdc_original','contextual_extra_trees','dboost_text_original','lucario_original_history']:
   t=z['truth'];fresh=z[method]&~u[method];extra=z[method]&~z[baseline];counter.append({**{k:d[k] for k in ['scenario','dataset','view','family','mechanism','rate','seed']},'baseline':baseline,'method':method,'extra_hits':int((extra&t).sum()),'newly_triggered_extra_hits':int((extra&fresh&t).sum()),'already_alerted_extra_hits':int((extra&u[method]&t).sum()),'newly_triggered_extra_alerts':int((extra&fresh).sum()),'untouched_detector_alerts':int(u[method].sum())})
m=pd.DataFrame(magnitudes);m.groupby(['dataset','family','mechanism','rate']).agg(changed_numeric_cells=('absolute','count'),median_absolute=('absolute','median'),min_absolute=('absolute','min'),max_absolute=('absolute','max'),median_relative=('relative','median'),median_history_IQR=('history_IQR_normalized','median'),zero_source_relative_undefined=('relative_undefined_zero_source','sum')).reset_index().to_csv(O/'severity_summary.csv',index=False);pd.DataFrame(counter).to_csv(O/'counterpart_increment.csv.gz',index=False,compression={'method':'gzip','mtime':0})
rows=[]
for p in sorted((O/'cdc_boundary/selected_cases').glob('*.json')):
 d=json.loads(p.read_text())
 for row in d['metrics']:rows.append({**{k:d[k] for k in ['scenario','dataset','mode','family']},'type_mode':d['mode'],**row})
pd.DataFrame(rows).to_csv(O/'cdc_boundary_metrics.csv',index=False)
rows=[]
for name in ['rt','st']:
 f=pd.read_csv(O/f'values/{name}_coordinate_outputs.csv.gz');truth=set(np.flatnonzero(f.publisher_positive&~f.ambiguous));amb=set(np.flatnonzero(f.ambiguous));pattern=set(np.flatnonzero(f.AutoTest_pattern_native));stat=set(np.flatnonzero(f.RS));full=set(np.flatnonzero(f.AutoTest_full));key=lambda i:hashlib.sha256(f'{name}:{f.iloc[i].column_position:.0f}:{f.iloc[i].value_position:.0f}'.encode()).digest();order=lambda s:sorted(s,key=key)
 for k in [25,50,100]:
  bs=set((order(pattern)+order(stat-pattern))[:k]);b=order(stat-pattern);d=order(full-pattern);tail=[i for pair in itertools.zip_longest(b,d) for i in pair if i is not None];s=set(list(dict.fromkeys(order(pattern)+tail))[:k]);rows.append({'benchmark':name,'policy':'pretrained_pattern_first_equal_share','capacity':k,'baseline_hits':len(bs&truth),'union_hits':len(s&truth),'net_hits':len(s&truth)-len(bs&truth),'extra_hits':len((s-bs)&truth),'lost_hits':len((bs-s)&truth),'reviewed':len(s),'ambiguous_reviews':len(s&amb),'status':'POSTHOC_EXPLORATORY_PRIORITY_SENSITIVITY','information':'Both comparator and advanced system have same released corpus pattern constraints; not hard business contracts'})
pd.DataFrame(rows).to_csv(O/'published_pattern_priority_sensitivity.csv',index=False)
(O/'diagnostic_analysis.json').write_text(json.dumps({'status':'EXECUTED','shared_row_donor_value_identical_across_mechanisms':True,'severity_design':'Scale .99/1.01 and fixed age+1 separate selection mechanism from fixed magnitude. Donor substitution severity depends on selected rows; not a fully crossed severity experiment.','counterpart_definition':'newly_triggered_extra_hits = truth AND advanced_changed AND NOT advanced_untouched AND NOT baseline_changed','canonical_CDC_native_parity':all(d['native_untouched_equals_primary'] for d in json.loads((O/'cdc_boundary/results.json').read_text()) if d['mode']=='native_types')},indent=2)+'\n');print(pd.DataFrame(rows).to_string(index=False))
