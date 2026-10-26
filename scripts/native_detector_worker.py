# SPDX-License-Identifier: GPL-3.0-or-later
# Original dBoost is imported only in this separate process; upstream sources stay ignored.
# LUCARIO/CDC code is imported from pinned local author checkouts, not redistributed.
import contextlib,json,sys,time,re,copy,traceback,os
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
import pandas as pd
STATE={}

def lucario_fit(df):
 from detectors.pattern import PatternDetector
 from detectors.range import RangeDetector
 from detectors.utils import Utils
 constraints={}
 for c in df:
  values=[v for v in df[c] if str(v) not in ['', 'NULL','None','N/A','NaN']]
  kind,values=Utils.column_type_constraint(values)
  rd=RangeDetector(values,.95,3);pd_=PatternDetector(values,.95)
  constraints[c]={'type_constraint':kind,'categorical_constraint':rd.categorical_range,'numerical_constraint':rd.numerical_range,'pattern_constraint':pd_.pattern_constraints}
 return constraints

def lucario_score(df,cons):
 from detectors.utils import Utils
 flags=[]
 for c in df:
  s=cons[c];typ=[];cat=[];num=[];pat=[]
  for v in df[c]:
   typ.append(Utils.type_anomaly_detector(v,s['type_constraint']))
   cat.append(True if v in ['', 'NULL','None','N/A','NaN'] else (s['categorical_constraint'] is not None and v not in s['categorical_constraint']))
   try:num.append(s['numerical_constraint'] is not None and (float(v)<s['numerical_constraint'][0] or float(v)>s['numerical_constraint'][1]))
   except (ValueError,TypeError):num.append(False)
   pat.append(bool(s['pattern_constraint']) and not any(re.fullmatch(p,str(v)) for p in s['pattern_constraint']))
  # Preserve upstream batch-dependent switch-off; learned range is NOT deleted for future batches.
  if np.mean(num)>.05:num=[False]*len(df)
  flags.append([bool(a or b or c_ or d) for a,b,c_,d in zip(typ,cat,num,pat)])
 return np.array(flags,dtype=bool).T

def dispatch(req):
 op=req['op'];method=req['method'];df=pd.DataFrame(req['rows'],columns=req['columns'])
 if op=='fit':
  targets=req['targets'];STATE.update(columns=req['columns'],targets=targets,method=method)
  if method.startswith('lucario'):
   source=Path(req['source']);sys.path.insert(0,str(source));STATE['constraints']=lucario_fit(df[targets]);return {'constraints':STATE['constraints'],'mode':'original inference classes including full pattern inference; native application parity checked separately; history fit is explicit regime change'}
  if method.startswith('dboost'):
   sys.path.insert(0,req['source']);import dboost
   from dboost import features
   from dboost.analyzers.statistical import Pearson
   from dboost.models.gaussian import Simple
   typed=method=='dboost_numeric_original';cat=req['categorical']
   def convert(frame):
    return [tuple(float(v) if typed and c not in cat else str(v) for c,v in zip(frame.columns,row)) for row in frame.itertuples(index=False,name=None)]
   tuples=convert(df);gen=lambda:iter(tuples);an=Pearson(.5);rules=features.rules;model=Simple(3)
   an.fit(dboost.expand_stream(gen,rules,False,None));an.expand_stats();model.fit(dboost.expand_stream(gen,rules,False,an.hints),an)
   STATE.update(an=an,model=model,rules=rules,convert=convert)
   return {'mode':'original Gaussian; reference fit; no row-dropping CSV reader used','typed':typed}
  if method=='cdc_original':
   sys.path.insert(0,req['source']);from conformal_data_cleaning.cleaner.conformal import ConformalAutoGluonCleaner
   for c in df:
    if c in req['categorical']:df[c]=df[c].astype('category')
    else:df[c]=pd.to_numeric(df[c],errors='raise')
   cleaner=ConformalAutoGluonCleaner(confidence_level=.95,seed=42)
   # Supported fit parameters reduce base-model/HPO compute; no replacement algorithm.
   cleaner.fit(df,target_columns=targets,ci_calibration_size=.25,ci_ag_predictor_params={'path_prefix':req['model_path'],'verbosity':0},ci_ag_fit_params={'hyperparameters':{'RF':{'n_estimators':40},'XT':{'n_estimators':40}},'num_cpus':1,'time_limit':30,'hyperparameter_tune_kwargs':{'num_trials':1}})
   STATE.update(cleaner=cleaner,categorical=req['categorical'])
   return {'native_categorical':cleaner._categorical_columns,'native_numerical':cleaner._numerical_columns,'regime':'untouched-source-history assumed usable, not independently clean; original guarantees not asserted'}
 if op=='score':
  if list(df)!=STATE['columns']:raise ValueError('Column alignment error')
  targets=STATE['targets']
  if method.startswith('lucario'):flags=lucario_score(df[targets],copy.deepcopy(STATE['constraints']))
  elif method.startswith('dboost'):
   import dboost
   from dboost.utils.printing import expand_hints
   tuples=STATE['convert'](df);flags=np.zeros((len(df),len(targets)),bool);an=STATE['an'];model=STATE['model'];col={c:j for j,c in enumerate(targets)}
   for i,row in enumerate(tuples):
    expanded=dboost.expand(row,STATE['rules']);expanded=dboost.expand_hints(expanded,an.hints) if an.hints is not None else expanded
    discrepancies=model.find_discrepancies(expanded,i)
    for group in discrepancies:
     for field,_ in expand_hints(group,an.hints):
      c=STATE['columns'][field]
      if c in col:flags[i,col[c]]=True
  else:
   for c in df:
    if c not in STATE['categorical']:df[c]=pd.to_numeric(df[c],errors='raise')
    else:df[c]=df[c].astype('category')
   # Original remove_outliers does not claim missing-value detection; native missingness remains non-outlier.
   _,flags,_=STATE['cleaner'].remove_outliers(df,empty_pred_sets_are_inliers=True)
   flags=flags[targets].to_numpy(bool)
  return {'flags':flags.tolist(),'shape':list(flags.shape),'binary_only':True}
 raise ValueError(op)

if __name__=='__main__':
 for line in sys.stdin:
  try:
   req=json.loads(line)
   with contextlib.redirect_stdout(sys.stderr):result=dispatch(req)
   print(json.dumps({'ok':True,'result':result},allow_nan=False,default=lambda x:x.item() if hasattr(x,'item') else str(x)),flush=True)
  except Exception as e:
   traceback.print_exc(file=sys.stderr);print(json.dumps({'ok':False,'error':repr(e)}),flush=True)
