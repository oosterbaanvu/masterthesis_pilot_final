"""Independent archive, placement, logged-value and arithmetic checks; no production imports."""
import argparse,collections,hashlib,io,itertools,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import xlrd
R=Path(__file__).resolve().parents[1];O=R/'results/sota_followup/ingest';checks=collections.Counter()
def require(ok,kind):
    if not ok:raise AssertionError(kind)
    checks[kind]+=1
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_source(name):
    if name=='credit':
        p=R/'data/recovery_downloads/default+of+credit+card+clients.zip'
        with zipfile.ZipFile(p) as z:
            s=xlrd.open_workbook(file_contents=z.read(next(n for n in z.namelist() if n.endswith('.xls')))).sheet_by_index(0)
            df=pd.DataFrame([s.row_values(i) for i in range(2,s.nrows)],columns=s.row_values(1));df=df.drop(columns=['ID',df.columns[-1]])
        cats=['SEX','EDUCATION','MARRIAGE','PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6']
        for c in cats:df[c]=df[c].map(lambda v:str(int(v)))
    elif name=='bank':
        p=R/'data/recovery_downloads/bank+marketing.zip'
        with zipfile.ZipFile(p) as z:
            with zipfile.ZipFile(io.BytesIO(z.read('bank-additional.zip'))) as zz:df=pd.read_csv(io.BytesIO(zz.read('bank-additional/bank-additional-full.csv')),sep=';').drop(columns='y')
    else:
        p=R/'data/pilot_sources/wine.zip'
        with zipfile.ZipFile(p) as z:df=pd.read_csv(io.BytesIO(z.read('winequality-white.csv')),sep=';').drop(columns='quality')
    for c in df:
        if pd.api.types.is_numeric_dtype(df[c]):df[c]=df[c].astype(float)
    df.index=[f'{name}:{i}' for i in range(len(df))]
    return df.astype(object),sha(p)
def coords(f):return set(map(tuple,np.argwhere(f)))
def order(f,ids,columns):return sorted(coords(f),key=lambda ij:hashlib.sha256(f'{ids[ij[0]]}|{columns[ij[1]]}'.encode()).digest())
def selected(h,b,d,k,policy):
    hs=set(h);bo=[x for x in b if x not in hs];do=[x for x in d if x not in hs]
    seq=bo+do if policy=='control_first' else [x for pair in itertools.zip_longest(bo,do) for x in pair if x is not None]
    return set(list(dict.fromkeys(h+seq))[:k])
def main(partial=False):
    sources={};cases=[]
    for path in sorted(O.glob('*.json')):
        d=json.loads(path.read_text())
        if 'scenario' not in d:continue
        cases.append(d);name=d['dataset'];view=d['view'];pop=json.loads((O/f'{name}_{view}_population.json').read_text());targets=pop['targets'];ids=pop['parts']['evaluation']
        if name not in sources:sources[name]=read_source(name)
        full,sourcehash=sources[name];require(sourcehash==d['source_sha256'],'source_bytes_identity')
        x=full.loc[ids];history=full.loc[pop['parts']['history']]
        require(not set(history.index)&set(ids),'historical_and_scored_ids_disjoint')
        require(not history.duplicated().any(),'unique_history_full_feature_vectors')
        logs=json.loads((R/d['log_path']).read_text());require(sha(R/d['log_path'])==d['log_sha256'],'logged_values_hash')
        z=np.load(O/(d['scenario']+'.npz'));require(sha(O/(d['scenario']+'.npz'))==d['prediction_sha256'],'saved_prediction_hash')
        changed=x.copy();expected=np.zeros((len(x),len(targets)),bool)
        for e in logs:
            require(str(x.at[e['row_id'],e['column']])==str(e['original']) and str(e['new'])!=str(e['original']),'original_and_changed_values')
            changed.at[e['row_id'],e['column']]=e['new'];expected[ids.index(e['row_id']),targets.index(e['column'])]=True
        require(np.array_equal(z['truth'],expected),'exact_truth_coordinates')
        require(not (z['R']&expected).any(),'nontrivial_changes_not_hard_contract_failures')
        require(np.all(~z['R']|z['RS']) and np.all(~z['RS']|z['RSM']),'baseline_nesting')
        info=d['diagnostics'];target=info['target'];condition=info['condition'];bins=pd.qcut(pd.to_numeric(x[condition]),4,duplicates='drop',labels=False);candidates={}
        for rid in ids:
            old=x.at[rid,target];op=info['operation'];param=info['parameter']
            if op=='period':new=x.at[rid,param]
            elif op=='scale':new=float(old)*param
            elif op=='offset':new=float(old)+param
            else:
                pool=x.loc[(bins==bins.loc[rid])&(x[target].astype(str)!=str(old)),target]
                if pool.empty:continue
                n=int(hashlib.sha256(f"{d['seed']}|{rid}|{d['family']}".encode()).hexdigest()[:16],16);new=pool.iloc[n%len(pool)]
            if str(new)!=str(old) and not (isinstance(old,(int,float)) and isinstance(new,(int,float)) and float(old)==float(new)):candidates[rid]=new
        require(len(candidates)==info['eligible'],'independent_eligible_count')
        for e in logs:require(str(candidates[e['row_id']])==str(e['new']),'independent_replacement_value')
        n=max(1,int(len(candidates)*d['rate']));eligible=x.loc[list(candidates)];rng=np.random.default_rng(d['seed'])
        if d['mechanism']=='ECAR':chosen=rng.choice(eligible.index,n,replace=False)
        else:
            c=condition if d['mechanism']=='EAR' else target;start=int(rng.integers(0,len(eligible)-n)) if len(eligible)>n else 0;chosen=eligible.sort_values(c).iloc[start:start+n].index
        require(n==len(logs)==info['realized'] and set(chosen)=={e['row_id'] for e in logs},'independent_mechanism_and_realized_count')
        t=coords(expected);untouched=np.load(O/f'{name}_{view}_untouched.npz')
        for m in d['metrics']:
            b=coords(z[m['baseline']]);a=coords(z[m['method']])
            if m['mode']=='budget_union':
                k=max(1,int(np.ceil(len(ids)*m['budget']/1000)));h=order(z['R'],ids,targets);bo=order(z[m['baseline']],ids,targets);s=selected(h,bo,order(z[m['method']],ids,targets),k,m['policy']);bs=selected(h,bo,[],k,m['policy'])
                require(m['reviewed']==len(s)<=k and m['hits']==len(s&t),'independent_review_capacity_and_hits')
                require(m['extra_hits']==len((s-bs)&t) and m['lost_hits']==len((bs-s)&t) and m['net_hits']==len(s&t)-len(bs&t),'independent_net_gain_and_displacement')
            else:
                s=a if m['mode']=='alone' else a|b
                require(m['hits']==len(s&t) and m['alerts']==len(s) and m['extra_hits']==len((s-b)&t) and m['extra_alerts']==len(s-b),'independent_unconstrained_increment')
                require(m['new_detector_hits']==len((a-coords(untouched[m['method']]))&t),'independent_new_triggered_hits')
        require(d['source_available_reconciliation']['hits']==len(t)==d['source_available_reconciliation']['alerts'],'upstream_source_reconciliation_complete')
    logical={tuple(d[k] for k in ['dataset','family','mechanism','rate','seed']) for d in cases}
    if not partial:require(len(cases)==720 and len(logical)==360,'full_frozen_grid_count')
    result={'status':'PASSED','context_cases':len(cases),'logical_cases':len(logical),'checks':dict(checks),'assertions':sum(checks.values()),'limitation':'Independent arithmetic and source-alteration evidence, not independent semantic annotation.'}
    (R/'evidence/sota_followup'/('ingest_smoke_verification.json' if partial else 'ingest_verification.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='checks'}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');main(p.parse_args().partial)
