import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge

class Encoder:
 def fit(self,df,cat):
  self.columns=list(df);self.cat=[c for c in cat if c in df];self.num=[c for c in df if c not in self.cat]
  transformers=[]
  if self.num:transformers.append(('numeric',make_pipeline(SimpleImputer(strategy='median'),StandardScaler()),self.num))
  if self.cat:transformers.append(('category',OneHotEncoder(handle_unknown='ignore',sparse_output=False),self.cat))
  self.pipeline=ColumnTransformer(transformers);self.pipeline.fit(self.prepare(df));return self
 def prepare(self,df):
  if list(df)!=self.columns:raise ValueError('Feature alignment mismatch')
  x=df.copy()
  for c in self.num:x[c]=pd.to_numeric(x[c],errors='coerce')
  for c in self.cat:x[c]=x[c].astype(str)
  return x
 def transform(self,df):return self.pipeline.transform(self.prepare(df))

class Controls:
 def __init__(self,contract,targets,cat):self.contract=contract;self.targets=targets;self.cat=cat
 def fit(self,history):
  self.columns=list(history);self.stats={};self.models={};self.provenance=[]
  fit=history.iloc[:int(.75*len(history))];cal=history.iloc[int(.75*len(history)):]
  for c in self.targets:
   if self.contract[c]['type']=='numeric':
    v=pd.to_numeric(history[c]);q=v.quantile([.005,.25,.75,.995]).to_numpy();iq=q[2]-q[1]
    self.stats[c]={'qlo':q[0],'qhi':q[3],'ilo':q[1]-3*iq,'ihi':q[2]+3*iq}
    others=[a for a in self.columns if a!=c];enc=Encoder().fit(fit[others],self.cat);reg=Ridge(alpha=10).fit(enc.transform(fit[others]),pd.to_numeric(fit[c]))
    errors=np.abs(reg.predict(enc.transform(cal[others]))-pd.to_numeric(cal[c]).to_numpy());cut=float(np.quantile(errors,.995,method='higher'))
    self.models[c]=(others,enc,reg,cut)
   else:self.stats[c]={'shares':history[c].astype(str).value_counts(normalize=True).to_dict()}
   self.provenance.append({'column':c,'control':'extended_profile_and_conditional_linear_residual','provenance':'TRAINING_ONLY_STATISTICAL_CONTROL','quantile':.995,'hard_validity':False,'fit_rows':len(fit),'calibration_rows':len(cal)})
  return self
 def score(self,df):
  if list(df)!=self.columns:raise ValueError('Incorrect feature alignment')
  a=np.zeros((len(df),len(self.targets)),bool);b=a.copy()
  for j,c in enumerate(self.targets):
   x=df[c];s=self.contract[c];miss=x.isna()|x.astype(str).isin(['','NULL'])
   if s['type']=='numeric':
    v=pd.to_numeric(x,errors='coerce').to_numpy(float);bad=~np.isfinite(v)
    if 'bounds' in s:
     lo,hi=s['bounds'];bad|=(v<lo) if lo is not None else False
     if hi is not None:bad|=v>hi
    a[:,j]=bad|miss.to_numpy();p=self.stats[c];stat=(v<p['qlo'])|(v>p['qhi'])|(v<p['ilo'])|(v>p['ihi'])
    others,enc,reg,cut=self.models[c];pred=reg.predict(enc.transform(df[others]));stat|=np.abs(v-pred)>cut
    b[:,j]=a[:,j]|stat
   else:
    a[:,j]=miss|~x.astype(str).isin(s['domain']);shares=x.astype(str).map(self.stats[c]['shares']).fillna(0);b[:,j]=a[:,j]|(shares.to_numpy()<.005)
  assert np.all(~a|b)
  return a,b
