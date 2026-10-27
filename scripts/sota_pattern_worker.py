"""Original source inference without importing the label-selecting benchmark harness."""
import ast,contextlib,hashlib,json,sys,time,traceback
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'data/sources/RIOLU';sys.path.insert(0,str(source))
tree=ast.parse((source/'Auto-RIOLU.py').read_text());nodes=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='dataset' for t in node.targets):break
    nodes.append(node)
namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source/'Auto-RIOLU.py'),'exec'),namespace)

def infer(values,seed):
    np.random.seed(seed);start=time.perf_counter();usable=[str(v) for v in values if v is not None]
    if len(usable)<2:return {'flags':[None]*len(values),'status':'NOT_APPLICABLE','reason':'fewer than two source values; no zero-score replacement'}
    small=len(sys.argv)>1 and sys.argv[1]=='riolu_small_sample'
    if len(usable)<385 and not small:return {'flags':[None]*len(values),'status':'NOT_APPLICABLE','reason':'Original defaults sample 385 without replacement; distinct-value population too small'}
    if small:
        original_generator=namespace.get('original_generator',namespace['PatternGenerator']);namespace['original_generator']=original_generator
        namespace['PatternGenerator']=lambda data,coverage:original_generator(data,coverage,sampling_size=min(385,len(data)))
    coverage=sum(namespace['coverage_estimation'](usable,.95) for _ in range(5))/5
    generator=namespace['PatternGenerator'](usable,coverage);generator.pattern_coverage_statictics();selector=namespace['PatternSelector'](generator.pattern_coverage,len(usable));selector.select_patterns();patterns=selector.pattern_pool
    flags=[bool(v is not None and not any(namespace['Utils'].pattern_matching(p,str(v)) for p in patterns)) for v in values]
    return {'flags':flags,'status':'EXPLICIT_ADAPTATION' if small else 'ORIGINAL_REPRODUCED','coverage_estimate':coverage,'patterns':len(patterns),'pattern_sha256':hashlib.sha256(json.dumps(patterns).encode()).hexdigest(),'seconds':time.perf_counter()-start,'labels_used':0,'unit':'input value occurrence, or distinct value when caller supplies unique values'}

def infer_lucario(values,seed):
    sys.path.insert(0,str(ROOT/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO'))
    sys.path.insert(0,str(ROOT/'scripts'))
    from native_detector_worker import lucario_fit,lucario_score
    import pandas as pd
    np.random.seed(seed);start=time.perf_counter();df=pd.DataFrame({'value':values});constraints=lucario_fit(df);flags=lucario_score(df,constraints)[:,0]
    return {'flags':flags.tolist(),'status':'ORIGINAL_REPRODUCED','seconds':time.perf_counter()-start,'labels_used':0,'regime':'native transductive inference on supplied distinct values; no occurrence frequency invented'}

if __name__=='__main__':
    for line in sys.stdin:
        try:
            request=json.loads(line)
            with contextlib.redirect_stdout(sys.stderr):result=(infer_lucario if len(sys.argv)>1 and sys.argv[1]=='lucario_transductive' else infer)(request['values'],request.get('seed',42))
            reply={'ok':True,'result':result}
        except Exception as e:
            traceback.print_exc(file=sys.stderr);reply={'ok':False,'error':repr(e)}
        print(json.dumps(reply),flush=True)
