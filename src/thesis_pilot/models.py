import json,os,select,subprocess,time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor,ExtraTreesClassifier
from .controls import Encoder
from .data import ROOT

class ContextualTrees:
 name='contextual_extra_trees'
 def fit(self,df,targets,cat):
  self.columns=list(df);self.targets=targets;self.models={};train=df.iloc[:int(.75*len(df))];cal=df.iloc[int(.75*len(df)):]
  for c in targets:
   others=[x for x in df if x!=c];enc=Encoder().fit(train[others],cat);X=enc.transform(train[others]);C=enc.transform(cal[others])
   categorical=c in cat
   cls=ExtraTreesClassifier if categorical else ExtraTreesRegressor
   model=cls(n_estimators=64,max_depth=16,min_samples_leaf=5,n_jobs=1,random_state=42).fit(X,train[c].astype(str) if categorical else pd.to_numeric(train[c]))
   if categorical:
    proba=model.predict_proba(C);lookup={str(v):i for i,v in enumerate(model.classes_)};scores=np.array([1-proba[i,lookup[str(v)]] if str(v) in lookup else 1 for i,v in enumerate(cal[c])])
   else:scores=np.abs(model.predict(C)-pd.to_numeric(cal[c]).to_numpy())
   self.models[c]=(others,enc,model,categorical,float(np.quantile(scores,.995,method='higher')))
  return self
 def score(self,df):
  if list(df)!=self.columns:raise ValueError('Model feature alignment')
  flags=[]
  for c in self.targets:
   others,enc,m,cat,cut=self.models[c];X=enc.transform(df[others])
   if cat:
    proba=m.predict_proba(X);lookup={str(v):i for i,v in enumerate(m.classes_)};score=np.array([1-proba[i,lookup[str(v)]] if str(v) in lookup else 1 for i,v in enumerate(df[c])])
   else:score=np.abs(m.predict(X)-pd.to_numeric(df[c],errors='coerce').to_numpy())
   flags.append(np.isfinite(score)&(score>cut))
  return np.array(flags).T
 def close(self):pass

class Native:
 def __init__(self,name,source,python):
  self.name=name;self.source=str(source);self.python=str(python);self.proc=None
 def call(self,payload,timeout=180):
  self.proc.stdin.write(json.dumps(payload,allow_nan=False)+'\n');self.proc.stdin.flush()
  if not select.select([self.proc.stdout],[],[],timeout)[0]:self.close();raise TimeoutError(self.name+' timed out')
  line=self.proc.stdout.readline()
  if not line:raise RuntimeError(self.name+' worker exited; inspect log')
  response=json.loads(line)
  if not response['ok']:raise RuntimeError(response['error'])
  return response['result']
 def fit(self,df,targets,cat,dataset):
  self.columns=list(df);self.targets=targets
  log=ROOT/'evidence/thesis_pilot'/f'{dataset}_{self.name}.log';self.log=log.open('w')
  env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='0')
  self.proc=subprocess.Popen([self.python,str(ROOT/'scripts/native_detector_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1,env=env)
  meta=self.call({'op':'fit','method':self.name,'source':self.source,'rows':df.values.tolist(),'columns':self.columns,'targets':targets,'categorical':cat,'model_path':str(ROOT/'data/pilot_models'/dataset/self.name)},timeout=420)
  (ROOT/'evidence/thesis_pilot'/f'{dataset}_{self.name}_fit.json').write_text(json.dumps(meta,indent=2))
  return self
 def score(self,df):
  result=self.call({'op':'score','method':self.name,'rows':df.values.tolist(),'columns':list(df)},timeout=90)
  flags=np.array(result['flags'],bool)
  if flags.shape!=(len(df),len(self.targets)):raise ValueError('Incomplete native output')
  return flags
 def close(self):
  if self.proc:
   self.proc.terminate()
   try:self.proc.wait(timeout=3)
   except subprocess.TimeoutExpired:self.proc.kill();self.proc.wait()
   self.proc=None
  if hasattr(self,'log'):self.log.close()
