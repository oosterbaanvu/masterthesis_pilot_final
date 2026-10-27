import argparse,gzip,hashlib,json,time
from pathlib import Path
import numpy as np
import pandas as pd
from thesis_pilot.data import ROOT
from sota_followup.benchmarks import load_benchmark,statistical_flags,AutoTestPattern
from sota_followup.models import PatternWorker,FollowupNative
from sota_followup.pattern_adapter import BoundedPatternWorker

def run(name,limit=None):
    out=ROOT/'results/sota_followup/values';out.mkdir(parents=True,exist_ok=True);rows,inventory=load_benchmark(name)
    (ROOT/f'manifests/sota_followup/{name}_qualification.json').write_text(json.dumps(inventory,indent=2)+'\n')
    if limit:rows=rows[:limit]
    methods={};start=time.perf_counter()
    for corpus in ['rt_train','st_train']:
        model=AutoTestPattern(corpus);flags,scores=model.score_columns(rows);methods['AutoTest_pattern_only_'+corpus]=(flags,scores)
    worker=BoundedPatternWorker();small_worker=BoundedPatternWorker('riolu_small_sample');lucario=BoundedPatternWorker('lucario_transductive');pred=[];status=[]
    checkpoint=ROOT/f'data/sota_followup/value_checkpoint_v3/{name}';checkpoint.mkdir(parents=True,exist_ok=True)
    code=hashlib.sha256(b''.join((ROOT/p).read_bytes() for p in ['src/sota_followup/benchmarks.py','src/sota_followup/pattern_adapter.py','scripts/sota_pattern_worker.py'])).hexdigest()
    try:
        for k,row in enumerate(rows):
            rid=row['position'];values=row['values'];results={}
            cp=checkpoint/(str(rid)+'.json');input_hash=hashlib.sha256(json.dumps(values).encode()).hexdigest()
            if cp.exists():
                saved=json.loads(cp.read_text())
                if saved['code_sha256']!=code or saved['input_sha256']!=input_hash:raise RuntimeError('Version value checkpoint before changing production inference')
                results=saved['results']
            else:
                for method,adapter in [('riolu_original',worker),('riolu_small_sample',small_worker),('lucario_transductive',lucario)]:
                    try:results[method]=adapter.score(values)
                    except Exception as error:results[method]={'status':'BLOCKED_SOFTWARE','error':repr(error),'flags':[None]*len(values)}
                cp.write_text(json.dumps({'code_sha256':code,'input_sha256':input_hash,'results':results}))
            riolu=results['riolu_original'];flags={'R':np.zeros(len(values),bool),'RS':statistical_flags(values),**{m:r['flags'] for m,r in results.items()}};conf={}
            for method,(f,s) in methods.items():flags[method]=f[rid];conf[method]=s[rid]
            for i,value in enumerate(values):
                record={'benchmark':name,'column_position':rid,'value_position':i,'publisher_positive':value in row['positive'],'ambiguous':value in row['ambiguous']}
                for method,f in flags.items():record[method]=None if f[i] is None else int(f[i])
                for method,s in conf.items():record[method+'_confidence']=float(s[i])
                pred.append(record)
            status.append({'column_position':rid,'methods':{m:{k:v for k,v in r.items() if k!='flags'} for m,r in results.items()}})
            if (k+1)%100==0:print(name,k+1,'columns complete',flush=True)
    finally:worker.close();small_worker.close();lucario.close()
    df=pd.DataFrame(pred);df.to_csv(out/f'{name}_patterns.csv.gz',index=False,compression={'method':'gzip','mtime':0})
    (out/f'{name}_patterns_status.json').write_text(json.dumps({'benchmark':name,'columns':len(rows),'values':len(df),'seconds':time.perf_counter()-start,'column_status':status,'unit':'distinct value','R':'No independently supplied hard column contract; empty finding set, not a claim that a mature enterprise has no controls.','RS':'fixed transductive type/quantile/IQR/coarse-shape heuristic; U0','RSM':'NOT_APPLICABLE: no relational row context','AutoTest':'pattern-only restricted family, U2, not full original Auto-Test'},indent=2));print(name,'DONE',len(rows),len(df),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--benchmarks',nargs='+',default=['rt','st']);p.add_argument('--limit',type=int);args=p.parse_args()
    for name in args.benchmarks:run(name,args.limit)
