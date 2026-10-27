import hashlib,json,os,subprocess
from pathlib import Path
from thesis_pilot.models import Native
from thesis_pilot.data import ROOT

class FollowupNative(Native):
    """Same original algorithms, isolated output/model directories."""
    def fit(self,df,targets,cat,dataset):
        self.columns=list(df);self.targets=targets
        evidence=ROOT/'evidence/sota_followup';evidence.mkdir(exist_ok=True)
        self.log=(evidence/f'{dataset}_{self.name}.log').open('w')
        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='0')
        self.proc=subprocess.Popen([self.python,str(ROOT/'scripts/native_detector_worker.py')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1,env=env)
        meta=self.call({'op':'fit','method':self.name,'source':self.source,'rows':df.values.tolist(),'columns':self.columns,'targets':targets,'categorical':cat,'model_path':str(ROOT/'data/sota_followup/models'/dataset/self.name)},timeout=420)
        if 'constraints' in meta:
            raw=json.dumps(meta).encode();p=ROOT/'data/sota_followup/models'/dataset/(self.name+'_constraints.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
            cons=meta.pop('constraints');meta['constraints_sha256']=hashlib.sha256(raw).hexdigest();meta['constraint_columns']=list(cons);meta['raw_constraints_retained_locally']=True
        (evidence/f'{dataset}_{self.name}_fit.json').write_text(json.dumps(meta,indent=2))
        return self

class PatternWorker:
    def __init__(self,method='riolu_original'):
        self.method=method
        p=ROOT/'evidence/sota_followup'/f'{method}_worker.log';self.log=p.open('a')
        self.proc=subprocess.Popen([str(ROOT/'data/envs/lucario/bin/python'),str(ROOT/'scripts/sota_pattern_worker.py'),method],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.log,text=True,bufsize=1,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
    def score(self,values,seed=42):
        self.proc.stdin.write(json.dumps({'values':list(values),'seed':seed})+'\n');self.proc.stdin.flush()
        import select
        if not select.select([self.proc.stdout],[],[],120)[0]:raise TimeoutError(self.method)
        line=self.proc.stdout.readline()
        if not line:raise RuntimeError('Pattern worker exited: inspect log')
        result=json.loads(line)
        if not result['ok']:raise RuntimeError(result['error'])
        return result['result']
    def close(self):
        self.proc.terminate();self.proc.wait(timeout=5);self.log.close()
