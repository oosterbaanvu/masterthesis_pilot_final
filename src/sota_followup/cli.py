import hashlib,json,os,subprocess,time
from pathlib import Path
import numpy as np
import pandas as pd
from thesis_pilot.data import ROOT
from .benchmarks import AutoTestPattern,statistical_flags,load_benchmark
from .pattern_adapter import BoundedPatternWorker

def metadata(method):
    registry={
        'riolu_original':{'citation':'Qin et al., ICSE2025, arXiv:2412.05240','commit':'df3f7dc7673fda3f02d147fdf4c539a2bf3cc4d5','license':'MIT code; data rights separate','status':'ORIGINAL_REPRODUCED','pretraining':'none','assumptions':'at least385 supplied values; auto coverage5rounds; default385 sample'},
        'riolu_small_sample':{'citation':'RIOLU supported parameter adaptation','commit':'df3f7dc7673fda3f02d147fdf4c539a2bf3cc4d5','license':'MIT code; data rights separate','status':'EXPLICIT_ADAPTATION','pretraining':'none','assumptions':'sampling_size=min(385,n); all other original inference stages retained'},
        'lucario_transductive':{'citation':'Qin et al., DOI10.1016/j.infsof.2026.108035','commit':'3664bfa830b7b13f8a08cc7dd960c871c56aaeeb','license':'No top-level license located; fetched source only, no redistribution','status':'ORIGINAL_LIMITED','pretraining':'none','assumptions':'native dirty-batch inference; default95% healthy coverage; known native template crashes recorded'},
        'autotest_pattern_only':{'citation':'Chen et al., SIGMOD2025, DOI10.1145/3725396','commit':'4acf65cf37a506206bf2888dbd45f17e58dce2e2','license':'No top-level license located; source/SDCs retained locally','status':'ORIGINAL_LIMITED_PATTERN_ABLATION','pretraining':'all60 published rt_train pattern SDCs; external corpus/source overlap not established','assumptions':'restricted original pattern preconditions and all-outlier reporting; not full Auto-Test'}}
    return {**registry[method],'unit':'actual source value occurrence, never invented row context','supported_types':['text','identifier','category'],'history':'not required; U0 for RIOLU/LUCARIO, U2 for pretrained Auto-Test subset','labels_consumed':0,'output':'binary suspicious coordinates; semantic correctness unknown','runtime_limit':'10s per column for native pattern worker; explicit resource failure, no zero score','business_rule_promotion':'NONE'}

def pattern_scan(args):
    record=json.loads((ROOT/'data/service_registry'/(args.id+'.json')).read_text());source=Path(record['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256'],'Registered file changed'
    frame=pd.read_csv(source,dtype=str,keep_default_na=False);contract=record['contract'];targets=contract.get('targets',list(contract['columns']));out=Path(args.output);out.mkdir(parents=True,exist_ok=True);findings=[];statuses=[];started=time.perf_counter()
    adapter=AutoTestPattern() if args.detector=='autotest_pattern_only' else BoundedPatternWorker(args.detector)
    try:
        for j,column in enumerate(targets):
            spec=contract['columns'][column]
            if spec['type'] not in ['text','identifier','category']:
                statuses.append({'column':column,'status':'NOT_APPLICABLE','reason':'This pattern adapter does not infer numeric regression semantics'});continue
            values=frame[column].tolist();hard=np.zeros(len(values),bool)
            if spec.get('required'):hard|=frame[column].isin(['','NULL']).to_numpy()
            if spec.get('domain'):hard|=~frame[column].isin(spec['domain']).to_numpy()
            try:
                if args.detector=='autotest_pattern_only':flags=adapter.score_columns([{'position':0,'header':column,'values':values}])[0][0].tolist();status={'status':'ORIGINAL_LIMITED_PATTERN_ABLATION'}
                else:
                    result=adapter.score(values);flags=result.pop('flags');status=result
                for i,flag in enumerate(flags):
                    if flag is not None and bool(flag):findings.append({'row_position':i,'column':column,'method':args.detector,'meaning':'pattern/statistical suspicion; semantic status unknown'})
            except Exception as e:status={'status':'BLOCKED_SOFTWARE','error':repr(e)}
            for name,flags in [('R',hard),('RS',hard|statistical_flags(values))]:
                for i in np.flatnonzero(flags):findings.append({'row_position':int(i),'column':column,'method':name,'meaning':'explicit contract finding' if name=='R' else 'profile suspicion'})
            statuses.append({'column':column,**status})
    finally:
        if hasattr(adapter,'close'):adapter.close()
    pd.DataFrame(findings,columns=['row_position','column','method','meaning']).to_csv(out/'findings.csv',index=False)
    eligible=sum(s['status'].startswith(('ORIGINAL','EXPLICIT')) for s in statuses)
    result={'source':args.id,'source_sha256':record['source_sha256'],'source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256'],'adapter':metadata(args.detector),'column_status':statuses,'eligible_columns':eligible,'alerts':len([f for f in findings if f['method']==args.detector]) if eligible else None,'seconds':time.perf_counter()-started,'recommendation':'INSUFFICIENT_EVIDENCE','reason':'Source scan has no oracle labels. No operational adoption from suspicious-pattern counts.'};(out/'report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

def benchmark_run(args):
    rows,_=load_benchmark(args.benchmark);p=ROOT/('data/sota_followup/autotest_input_'+args.benchmark+'.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps([{k:r[k] for k in ['position','header','values']} for r in rows]))
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONHASHSEED='13',TF_CPP_MIN_LOG_LEVEL='2',HF_HOME=str(ROOT/'data/huggingface'),TORCH_HOME=str(ROOT/'data/torch_cache'),TRANSFORMERS_CACHE=str(ROOT/'data/huggingface/transformers'),NLTK_DATA=str(ROOT/'data/nltk_data'),MPLCONFIGDIR=str(ROOT/'data/matplotlib'))
    cmd=[str(ROOT/'data/envs/autotest37/bin/python'),str(ROOT/'scripts/sota_autotest_full.py'),'--benchmark',args.benchmark,'--corpus',args.corpus]
    if args.limit:cmd+=['--limit',str(args.limit)]
    result=subprocess.run(cmd,env=env,cwd=ROOT);raise SystemExit(result.returncode)
