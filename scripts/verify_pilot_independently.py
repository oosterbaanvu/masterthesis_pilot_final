"""Independent original-byte, intervention, set-metric and capacity implementation.
Does not import thesis_pilot, its injector, detectors or metric/scheduling code.
"""
import collections,hashlib,io,itertools,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import xlrd
R=Path(__file__).resolve().parents[1]
checks=collections.Counter();mechanisms=[];groupmeta={}
def require(ok,kind):
 if not ok:raise AssertionError(kind)
 checks[kind]+=1

def original(name):
 if name=='credit':
  p=R/'data/recovery_downloads/default+of+credit+card+clients.zip'
  with zipfile.ZipFile(p) as z:
   s=xlrd.open_workbook(file_contents=z.read(next(x for x in z.namelist() if x.endswith('.xls')))).sheet_by_index(0)
   data=pd.DataFrame([s.row_values(i) for i in range(2,s.nrows)],columns=s.row_values(1));data=data.drop(columns=['ID',data.columns[-1]])
 elif name=='bank':
  p=R/'data/recovery_downloads/bank+marketing.zip'
  with zipfile.ZipFile(p) as z:
   with zipfile.ZipFile(io.BytesIO(z.read('bank-additional.zip'))) as zz:data=pd.read_csv(io.BytesIO(zz.read('bank-additional/bank-additional-full.csv')),sep=';').drop(columns='y')
 else:
  p=R/'data/pilot_sources/wine.zip'
  with zipfile.ZipFile(p) as z:data=pd.read_csv(io.BytesIO(z.read('winequality-white.csv')),sep=';').drop(columns='quality')
 pop=json.loads((R/'results/thesis_pilot'/(name+'_population.json')).read_text());contract=json.loads((R/'results/thesis_pilot'/(name+'_contracts.json')).read_text())['contract']
 require(hashlib.sha256(p.read_bytes()).hexdigest()==pop['source_sha256'],'source_hash')
 for c in data:
  if contract[c]['type']=='category':data[c]=data[c].map(lambda v:str(int(v)) if isinstance(v,(float,int)) and float(v).is_integer() else str(v))
  else:data[c]=pd.to_numeric(data[c]).astype(float)
 data.index=[f'{name}:{i}' for i in range(len(data))];data=data.astype(object)
 groups=pd.util.hash_pandas_object(data,index=False).astype(str)
 require(groups.loc[pop['parts']['history']].is_unique,'history_known_group_uniqueness_before_internal_calibration')
 for a,b in itertools.combinations(pop['parts'],2):require(not(set(groups.loc[pop['parts'][a]])&set(groups.loc[pop['parts'][b]])),'group_split_disjoint')
 require(set(pop['feature_columns'])==set(data),'outcome_exclusion_and_columns')
 eval_ids=pop['parts']['evaluation'];groupmeta[name]={'row_ids':eval_ids,'groups':groups.loc[eval_ids].tolist()}
 return data.loc[eval_ids,pop['evaluated_targets']],pop,contract

sources={n:original(n) for n in ['credit','bank','wine']}

def order(flags,rows,targets):
 return sorted(set(map(tuple,np.argwhere(flags))),key=lambda x:hashlib.sha256(f'{rows[x[0]]}|{targets[x[1]]}'.encode()).digest())

def reviewed(base,det,k,policy):
 if policy=='control_first':seq=base+det
 else:seq=[x for pair in itertools.zip_longest(base,det) for x in pair if x is not None]
 unique=list(dict.fromkeys(seq));return set(unique[:k])

expected=0;raw_rows=0;failures=collections.Counter();per_dataset=collections.Counter();per_family=collections.Counter();pred_methods=collections.Counter()
for path in sorted((R/'results/thesis_pilot/scenarios').glob('*.json')):
 d=json.loads(path.read_text());name=d['dataset'];df,pop,contract=sources[name];targets=list(df);rows=list(df.index);sid=d['scenario'];expected+=1;per_dataset[name]+=1;per_family[d['family']]+=1
 npz=R/'results/thesis_pilot/predictions'/(sid+'.npz');require(hashlib.sha256(npz.read_bytes()).hexdigest()==d['predictions_sha256'],'prediction_hash')
 logpath=R/d['injection_log'];require(hashlib.sha256(logpath.read_bytes()).hexdigest()==d['injection_log_sha256'],'injection_log_hash');logs=json.loads(logpath.read_text());cells=set();selected=[]
 for entry in logs:
  i=rows.index(entry['source_row_id']);j=targets.index(entry['column']);cells.add((i,j));selected.append(entry['source_row_id']);before=df.iloc[i,j];after=entry['new'];require(str(before)==entry['original'],'original_value_and_identity');require(str(before)!=after,'no_noops')
  if d['family']=='E4_scale':require(float(after)==float(before)*10 and float(before)!=0,'scale_operation')
  elif d['family']=='E1_missing':require(after=='' and contract[entry['column']]['required'],'requiredness_operation')
  elif d['family']=='E2_type':
   try:float(after);numeric=True
   except ValueError:numeric=False
   require(not numeric and contract[entry['column']]['type']=='numeric','lexical_operation')
  elif d['family']=='E3_code':require(after not in contract[entry['column']]['domain'],'invalid_domain_operation')
  elif d['family']=='E5_substitution':require(after in set(df[entry['column']].map(str)),'plausible_substitution_operation')
 require(len(cells)==len(logs)==d['diagnostics']['realized']==d['diagnostics']['intended'],'exact_injection_counts')
 target=d['target'];eligible=df[target].notna()&(df[target].astype(str)!='')
 if d['family']=='E4_scale':eligible&=pd.to_numeric(df[target])!=0
 sub=df.loc[eligible].copy();n=max(1,int(len(sub)*d['rate']));rng=np.random.default_rng(d['seed'])
 if d['mechanism']=='ECAR':chosen=rng.choice(sub.index,n,replace=False)
 else:
  cond=logs[0]['conditioning_variable']
  if contract[cond]['type']=='numeric':sub[cond]=pd.to_numeric(sub[cond])
  start=int(rng.integers(0,len(sub)-n)) if len(sub)>n else 0;chosen=sub.sort_values(cond).iloc[start:start+n].index
 require(set(chosen)==set(selected),'independent_mechanism_placement')
 z=np.load(npz);truth=set(map(tuple,np.argwhere(z['truth'])));require(truth==cells,'saved_truth_coordinates')
 orig=np.load(R/'results/thesis_pilot/predictions'/(name+'_untouched.npz'))
 for f in d['failures']:failures[f['method']+'|'+f['status']]+=1
 for method in z.files:
  if method!='truth':require(z[method].shape==z['truth'].shape,'complete_prediction_population');pred_methods[method]+=1
 for metric in d['metrics']:
  raw_rows+=1;base=metric['baseline'];method=metric['method'];bs=set(map(tuple,np.argwhere(z[base])));ds=set(map(tuple,np.argwhere(z[method])));assert method in z.files
  if metric['mode']=='budget_union':
   k=int(np.ceil(metric['budget_per_1000']*len(df)/1000));chosen=reviewed(order(z[base],rows,targets),order(z[method],rows,targets),k,metric['policy']);basechosen=set(order(z[base],rows,targets)[:k]);h=len(chosen&truth);bh=len(basechosen&truth)
   require(h==metric['hits'] and len(chosen)==metric['reviewed'] and len(chosen)<=k,'independent_budget_and_hits')
   require(metric['net_hits']==h-bh and metric['lost_baseline_hits']==len((basechosen-chosen)&truth),'independent_displacement')
  else:
   flags=ds if metric['mode']=='alone' else bs|ds;un=set(map(tuple,np.argwhere(orig[method])))
   if metric['mode']=='union':un|=set(map(tuple,np.argwhere(orig[base])))
   require(metric['hits']==len(flags&truth) and metric['alerts']==len(flags),'independent_unconstrained_metrics')
   require(metric['newly_triggered_hits']==len((flags-un)&truth),'independent_newly_triggered_hits')
   require(metric['additional_hits']==len((flags-bs)&truth) and metric['additional_alerts']==len(flags-bs),'independent_incremental_metrics')
 mechanism=d['mechanism'];mechanisms.append({'scenario':sid,'dataset':name,'family':d['family'],'mechanism':mechanism,**d['diagnostics']})
require(expected==630,'full_predeclared_scenario_count')
pd.DataFrame(mechanisms).to_csv(R/'results/thesis_pilot/injection_validation.csv',index=False)
(R/'results/thesis_pilot/source_group_metadata.json').write_text(json.dumps(groupmeta,indent=2))
summary={'status':'PASSED','scenarios':expected,'metric_rows':raw_rows,'checks':dict(checks),'datasets':dict(per_dataset),'families':dict(per_family),'method_scenario_coverage':dict(pred_methods),'inapplicabilities_and_failures':dict(failures),'limitations':'Independent implementation of acquisition/splitting/intervention/evaluation arithmetic, not independent human annotation. No seed-based source-population significance claim.'}
(R/'evidence/thesis_pilot/independent_verification.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
