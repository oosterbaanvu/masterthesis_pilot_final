"""New source-relative experiments; no historical outputs are rewritten."""
import argparse,hashlib,json,time,os
from pathlib import Path
import numpy as np
from thesis_pilot.data import ROOT,SPECS,load,contracts
from thesis_pilot.models import ContextualTrees
from sota_followup.layers import Layers
from sota_followup.models import FollowupNative
from sota_followup.interventions import CASES,alter
from sota_followup.metrics import evaluate

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def run(name,view,smoke=False):
    out=ROOT/'results/sota_followup/ingest';out.mkdir(parents=True,exist_ok=True)
    local=ROOT/'data/sota_followup/injections';local.mkdir(parents=True,exist_ok=True)
    parts,pop=load(name);targets=SPECS[name]['targets'];columns=targets if view=='narrow' else list(parts['history']);history=parts['history'][columns];source=parts['evaluation'][columns];cats=[c for c in SPECS[name]['categorical'] if c in columns]
    contract=contracts(name,parts['history']);rules=Layers(contract,targets,cats).fit(history);original=rules.score_layers(source)
    models=[ContextualTrees(),FollowupNative('cdc_original',Path('/workspace/research_sources/se-jaeger__conformal-data-cleaning'),ROOT/'data/envs/cdc/bin/python'),FollowupNative('lucario_original_history',ROOT/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO',ROOT/'data/envs/lucario/bin/python'),FollowupNative('dboost_text_original',ROOT/'data/sources/cpitclaudel__dBoost',ROOT/'data/envs/pilot/bin/python')]
    fitted=[];status=[]
    for model in models:
        start=time.perf_counter()
        try:
            if isinstance(model,FollowupNative):model.fit(history,targets,cats,f'ingest_{name}_{view}')
            else:model.fit(history,targets,cats)
            original[model.name]=model.score(source);fitted.append(model);status.append({'method':model.name,'status':'EXECUTED','fit_and_original_seconds':time.perf_counter()-start,'untouched_alerts':int(original[model.name].sum())})
        except Exception as error:
            status.append({'method':model.name,'status':'BLOCKED','error':repr(error)});model.close()
    (out/f'{name}_{view}_population.json').write_text(json.dumps({'source':name,'view':view,'feature_columns':columns,'targets':targets,'parts':pop['parts'],'source_sha256':pop['source_sha256'],'model_status':status,'regime':'U1; same unlabelled history; not certified clean'},indent=2))
    np.savez_compressed(out/f'{name}_{view}_untouched.npz',**original)
    protocol=ROOT/'configs/sota_followup/ingest_v2.json'
    files=[ROOT/f'src/sota_followup/{x}.py' for x in ['interventions','layers','models','metrics']]+[Path(__file__),ROOT/'scripts/native_detector_worker.py']
    code=hashlib.sha256(b''.join(p.read_bytes() for p in files)).hexdigest();count=0
    try:
        for case in CASES[name]:
            for mechanism in (['ECAR'] if smoke else ['ECAR','EAR','ENAR']):
                for rate in ([.05] if smoke else [.01,.05,.1]):
                    for seed in ([101] if smoke else [101,202,303,404,505]):
                        sid=f'{name}_{case[0]}_{mechanism}_{int(rate*100)}_{seed}_{view}';path=out/(sid+'.json')
                        if path.exists():
                            prior=json.loads(path.read_text())
                            if prior['code_sha256']!=code or prior['protocol_sha256']!=digest(protocol):raise RuntimeError('Version checkpoint before changing frozen code: '+sid)
                            count+=1;continue
                        # Original full source is available only to the injector/evaluator, not detector inputs.
                        condition=SPECS[name]['condition']
                        if condition==case[1]:condition='alcohol' if name=='wine' else 'duration'
                        changed,logs,info=alter(parts['evaluation'],case,mechanism,rate,seed,condition);current=changed[columns]
                        truth=np.zeros((len(source),len(targets)),bool)
                        for entry in logs:truth[source.index.get_loc(entry['row_id']),targets.index(entry['column'])]=True
                        predictions=rules.score_layers(current);timing={};failures=[]
                        for model in fitted:
                            start=time.perf_counter()
                            try:predictions[model.name]=model.score(current)
                            except Exception as error:failures.append({'method':model.name,'status':'BLOCKED','error':repr(error)})
                            timing[model.name]=time.perf_counter()-start
                        assert not predictions['R'][truth].any(),'Non-trivial alteration unexpectedly violates hard target contract'
                        # A source-available reconciliation baseline gets its own oracle-access regime.
                        source_reconciliation=(current[targets].astype(str)!=source[targets].astype(str)).to_numpy()
                        assert np.array_equal(source_reconciliation,truth)
                        npz=out/(sid+'.npz');np.savez_compressed(npz,truth=truth,**predictions)
                        lp=local/(sid+'.json');lp.write_text(json.dumps(logs))
                        record={'scenario':sid,'dataset':name,'view':view,'family':case[0],'mechanism':mechanism,'rate':rate,'seed':seed,'information_regime':'U1','truth_category':'B_SOURCE_RELATIVE_INGEST_ALTERATION','source_sha256':pop['source_sha256'],'code_sha256':code,'protocol_sha256':digest(protocol),'prediction_sha256':digest(npz),'log_path':str(lp.relative_to(ROOT)),'log_sha256':digest(lp),'diagnostics':info,'failures':failures,'timing':timing,'source_available_reconciliation':{'regime':'upstream snapshot available to both rules and evaluation','hits':len(logs),'alerts':len(logs),'additional_detector_hits_possible':0},'metrics':evaluate(predictions,original,truth,list(source.index),targets)}
                        path.write_text(json.dumps(record,separators=(',',':')));count+=1
                        if count%15==0:print(name,view,count,'completed',flush=True)
    finally:
        for model in fitted:model.close()
    print(name,view,'DONE',count,flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--datasets',nargs='+',default=['credit','bank','wine']);parser.add_argument('--views',nargs='+',default=['narrow','full']);parser.add_argument('--smoke',action='store_true');args=parser.parse_args()
    for name in args.datasets:
        for view in args.views:run(name,view,args.smoke)
