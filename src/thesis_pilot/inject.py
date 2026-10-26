import hashlib,random
import numpy as np
import pandas as pd
from tab_err.error_mechanism import ECAR,EAR,ENAR
from .data import SPECS

def scenarios(name):
 s=SPECS[name];out=[('E1_missing',s['amount'],'','VERIFIED_OPERATIONAL_ERROR'),('E2_type',s['numeric_target'],'INVALID_NUMERIC','VERIFIED_OPERATIONAL_ERROR'),('E4_scale',s['amount'],10.0,'CONTROLLED_ALTERATION'),('E5_substitution',s['numeric_target'],None,'CONTROLLED_ALTERATION')]
 if s['category']:out.append(('E3_code',s['category'],'99' if name=='credit' else '__INVALID_CODE__','VERIFIED_OPERATIONAL_ERROR'))
 return out

def inject(df,name,case,mechanism,rate,seed):
 family,target,param,label=case;s=SPECS[name];j=list(df).index(target);orig=df[target];rng=np.random.default_rng(seed)
 if family=='E4_scale':eligible=pd.to_numeric(orig,errors='coerce').notna()&(pd.to_numeric(orig,errors='coerce')!=0)
 else:eligible=orig.notna()&(orig.astype(str)!='')
 eligible_ids=orig.index[eligible];n=max(1,int(len(eligible_ids)*rate));sub=df.loc[eligible_ids].copy();cond=s['condition']
 if cond==target:cond=next(c for c in df if c!=target and c not in s['categorical'])
 # All selection depends only on immutable original pre-intervention rows.
 # tab_err uses numeric/string source ordering, not corrupted values.
 for c in sub:
  if c not in s['categorical']:sub[c]=pd.to_numeric(sub[c],errors='raise')
 cls={'ECAR':ECAR,'EAR':EAR,'ENAR':ENAR}[mechanism]
 kwargs={'seed':seed}
 if mechanism=='EAR':kwargs['condition_to_column']=cond
 state=random.getstate()
 try:mask=cls(**kwargs).sample(sub,target,(n+.25)/len(sub))
 finally:random.setstate(state)
 ids=mask.index[mask[target]];assert len(ids)==n
 new=df.copy();logs=[]
 for row_id in ids:
  before=orig.loc[row_id]
  if family=='E4_scale':after=float(before)*param
  elif family=='E5_substitution':
   pool=orig[orig.astype(str)!=str(before)].to_numpy();assert len(pool)
   rr=np.random.default_rng(int(hashlib.sha256(f'{seed}|{row_id}|donor'.encode()).hexdigest()[:12],16));after=pool[rr.integers(len(pool))]
  else:after=param
  assert str(after)!=str(before),'No-op injection'
  new.at[row_id,target]=after
  logs.append({'source_row_id':row_id,'column':target,'original':str(before),'new':str(after),'family':family,'mechanism':mechanism,'conditioning_variable':cond if mechanism=='EAR' else (target if mechanism=='ENAR' else None),'rate':rate,'eligible_count':len(eligible_ids),'intended_count':n,'realized_count':n,'severity':param,'seed':seed,'label_status':label,'contract':'operational required/type/domain' if label=='VERIFIED_OPERATIONAL_ERROR' else None})
 actual=(new.astype(str)!=df.astype(str)).to_numpy();assert actual.sum()==n;assert actual[:,j].sum()==n
 diagnostics={'eligible':len(eligible_ids),'intended':n,'realized':n,'actual_rate':n/len(eligible_ids),'conditioning_rank_mean':None,'target_rank_mean':None}
 for c,key in [(cond,'conditioning_rank_mean'),(target,'target_rank_mean')]:
  ranks=sub[c].rank(method='average',pct=True);diagnostics[key]=float(ranks.loc[ids].mean())
 return new,logs,diagnostics
