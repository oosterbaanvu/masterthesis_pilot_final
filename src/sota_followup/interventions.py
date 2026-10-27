"""Source-relative alterations; these logs do not certify semantic correctness."""
import random
import numpy as np
import pandas as pd
from tab_err.error_mechanism import ECAR,EAR,ENAR

CASES = {
 'credit': [('P2_wrong_period','BILL_AMT1','period','BILL_AMT2'),('P4_valid_category','EDUCATION','category',None)],
 'bank': [('P1_context_donor','duration','donor',None),('P4_valid_category','job','category',None),('P6_systematic_offset','age','offset',1)],
 'wine': [('P1_context_donor','alcohol','donor',None),('P3_scale_101','density','scale',1.01),('P3_scale_099','density','scale',.99)]}

def alter(frame, case, mechanism, rate, seed, condition):
    family,target,operation,parameter=case
    replacements={}
    conditioning=frame[condition]
    # Donors are selected within fixed unlabeled conditioning-quantile bins.
    bins=pd.qcut(pd.to_numeric(conditioning),4,duplicates='drop',labels=False)
    for rid in frame.index:
        old=frame.at[rid,target]
        digest=int(__import__('hashlib').sha256(f'{seed}|{rid}|{family}'.encode()).hexdigest()[:16],16)
        if operation=='period':new=frame.at[rid,parameter]
        elif operation=='scale':new=float(old)*parameter
        elif operation=='offset':new=float(old)+parameter
        else:
            pool=frame.loc[(bins==bins.loc[rid]) & (frame[target].astype(str)!=str(old)),target]
            if pool.empty:continue
            new=pool.iloc[digest%len(pool)]
        if str(new)!=str(old) and not (isinstance(old,(float,int)) and isinstance(new,(float,int)) and float(new)==float(old)):
            replacements[rid]=new
    eligible=frame.loc[list(replacements)].copy()
    n=max(1,int(len(eligible)*rate))
    if not len(eligible):raise ValueError('No non-noop eligible source values')
    state=random.getstate()
    try:
        kwargs={'seed':seed}
        if mechanism=='EAR':kwargs['condition_to_column']=condition
        mask={'ECAR':ECAR,'EAR':EAR,'ENAR':ENAR}[mechanism](**kwargs).sample(eligible,target,(n+.1)/len(eligible) if n<len(eligible) else 1.)
    finally:random.setstate(state)
    selected=mask.index[mask[target]]
    result=frame.copy();logs=[]
    for rid in selected:
        new=replacements[rid];old=frame.at[rid,target];result.at[rid,target]=new
        logs.append({'row_id':rid,'column':target,'original':old,'new':new})
    delta=(result.astype(str)!=frame.astype(str)).to_numpy()
    assert len(selected)==n==delta.sum()
    info={'eligible':len(eligible),'intended':n,'realized':len(logs),'realized_rate':n/len(eligible),'condition':condition,'family':family,'target':target,'operation':operation,'parameter':parameter,'label_status':'SOURCE_RELATIVE_INGEST_ALTERATION','semantic_correctness':'UNKNOWN'}
    return result,logs,info
