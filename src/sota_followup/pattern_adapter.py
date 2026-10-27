"""Bound original pattern inference without ever reusing a late response."""
import json,select,os
from sota_followup.models import PatternWorker

class BoundedPatternWorker(PatternWorker):
    def __init__(self,method='riolu_original',timeout=10):
        self.timeout=timeout
        self.start(method)
    def start(self,method):
        prior=os.environ.get('PYTHONHASHSEED');os.environ['PYTHONHASHSEED']='0'
        try:PatternWorker.__init__(self,method)
        finally:
            if prior is None:os.environ.pop('PYTHONHASHSEED',None)
            else:os.environ['PYTHONHASHSEED']=prior
    def score(self,values,seed=42):
        def reset():
            self.close();self.start(self.method)
        try:
            self.proc.stdin.write(json.dumps({'values':list(values),'seed':seed})+'\n');self.proc.stdin.flush()
            if not select.select([self.proc.stdout],[],[],self.timeout)[0]:
                reset();return {'flags':[None]*len(values),'status':'BLOCKED_RESOURCE','reason':'Native regex/inference exceeded fixed per-column wall bound','seconds_bound':self.timeout}
            line=self.proc.stdout.readline()
            if not line:reset();raise RuntimeError('Native worker exited; fresh worker created')
            response=json.loads(line)
            if not response['ok']:raise RuntimeError(response['error'])
            result=response['result']
            if len(result['flags'])!=len(values):reset();raise ValueError('Native coordinate arity mismatch')
            result['python_hash_seed']=0
            return result
        except (BrokenPipeError,EOFError):
            reset();raise
