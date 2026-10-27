"""Post hoc declared gap repair: add a cheap categorical predictor without rerunning detectors."""
import json,time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from thesis_pilot.data import ROOT,SPECS,load
from thesis_pilot.controls import Encoder
from sota_followup.metrics import evaluate
O=ROOT/'results/sota_followup';D=O/'categorical_baseline';D.mkdir(exist_ok=True);records=[];registry=[]
for name in ['credit','bank','wine']:
 for view in ['narrow','full']:
    pop=json.loads((O/f'ingest/{name}_{view}_population.json').read_text());parts,_=load(name);columns=pop['feature_columns'];targets=pop['targets'];history=parts['history'][columns];original=parts['evaluation'][columns];cat=[c for c in SPECS[name]['categorical'] if c in columns];n=int(.75*len(history));models={}
    for target in targets:
        if target not in cat:continue
        other=[c for c in columns if c!=target];encoder=Encoder().fit(history.iloc[:n][other],cat);model=LogisticRegression(C=1,max_iter=500,random_state=42,n_jobs=1).fit(encoder.transform(history.iloc[:n][other]),history.iloc[:n][target].astype(str));lookup={v:i for i,v in enumerate(model.classes_)}
        prob=model.predict_proba(encoder.transform(history.iloc[n:][other]));scores=np.array([1-prob[i,lookup[v]] if v in lookup else 1 for i,v in enumerate(history.iloc[n:][target].astype(str))]);cuts={str(q):float(np.quantile(scores,q,method='higher')) for q in [.95,.995]};models[target]=(other,encoder,model,lookup,cuts)
        registry.append({'dataset':name,'view':view,'target':target,'algorithm':'LogisticRegression','C':1,'max_iter':500,'seed':42,'fit_rows':n,'calibration_rows':len(history)-n,'cuts':cuts,'reference':'original source values, not verified-clean error labels','provenance':'TRAINING_ONLY_STATISTICAL_CONTROL threshold; explicit learned comparator, not hard rule'})
    def score(frame,q):
        flags=np.zeros((len(frame),len(targets)),bool)
        for target,(other,encoder,model,lookup,cuts) in models.items():
            prob=model.predict_proba(encoder.transform(frame[other]));values=frame[target].astype(str);s=np.array([1-prob[i,lookup[v]] if v in lookup else 1 for i,v in enumerate(values)]);flags[:,targets.index(target)]=s>cuts[str(q)]
        return flags
    originals=np.load(O/f'ingest/{name}_{view}_untouched.npz');original_add={q:score(original,q) for q in [.95,.995]}
    np.savez_compressed(D/f'{name}_{view}_untouched.npz',RSM_LR95=originals['RSM']|original_add[.95],RSM_LR995=originals['RSM']|original_add[.995])
    for path in sorted((O/'ingest').glob(name+'_*_'+view+'.json')):
        d=json.loads(path.read_text())
        if 'scenario' not in d:continue
        z=np.load(O/'ingest'/(d['scenario']+'.npz'));frame=original.copy();logs=json.loads((ROOT/d['log_path']).read_text())
        for e in logs:frame.at[e['row_id'],e['column']]=e['new']
        add={q:score(frame,q) for q in [.95,.995]};pred={q:z['RSM']|a for q,a in add.items()};np.savez_compressed(D/(d['scenario']+'.npz'),RSM_LR95=pred[.95],RSM_LR995=pred[.995])
        assert np.all(~pred[.995]|pred[.95]) and np.all(~z['RSM']|pred[.995])
        for q in [.95,.995]:
            label='RSM_LR95' if q==.95 else 'RSM_LR995';ps={k:z[k] for k in z.files if k!='truth'};ps['RSM_Ridge']=ps['RSM'];ps['RSM']=pred[q];us={k:originals[k] for k in originals.files};us['RSM_Ridge']=us['RSM'];us['RSM']=originals['RSM']|original_add[q]
            for row in evaluate(ps,us,z['truth'],pop['parts']['evaluation'],targets):
                if row['baseline']!='RSM':continue
                row['baseline']=label
                if row['method']=='RSM':row['method']=label
                records.append({**{k:d[k] for k in ['scenario','dataset','view','family','mechanism','rate','seed']},**row})
    print(name,view,'categorical comparator sensitivity completed',flush=True)
pd.DataFrame(records).to_csv(D/'metrics.csv.gz',index=False,compression={'method':'gzip','mtime':0});(D/'fit_registry.json').write_text(json.dumps({'status':'EXECUTED_EXPLORATORY_SENSITIVITY','models':registry,'reason':'Historical Ridge covers only numeric targets. Add explicit cheap categorical prediction without renaming old RSM or changing old detector flags.','operating_points':'Both95% and99.5% history-calibrated nonconformity cutoffs are reported; neither selected on test labels.'},indent=2)+'\n')
