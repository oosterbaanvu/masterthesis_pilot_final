"""Released CDC numeric endpoints on real untouched UCI inputs; no truth certification."""
import contextlib,json,os,sys,time
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'src'));sys.path.insert(0,'/workspace/research_sources/se-jaeger__conformal-data-cleaning')
from conformal_data_cleaning.cleaner.conformal import ConformalAutoGluonCleaner
from sota_followup.metrics import evaluate
O=R/'results/sota_followup/cdc_boundary';O.mkdir(exist_ok=True);records=[];original_guess=ConformalAutoGluonCleaner._guess_dtypes
for name in ['credit','bank','wine']:
    bridge=json.loads((R/f'data/sota_followup/{name}_canonical_frames.json').read_text());targets=bridge['targets'];cats=bridge['categories'];history=pd.DataFrame(bridge['history_values'],columns=bridge['columns']);batch=pd.DataFrame(bridge['evaluation_values'],columns=bridge['columns']);ids=bridge['evaluation_ids'];positions={rid:i for i,rid in enumerate(ids)}
    for df in [history,batch]:
        for c in df:
            df[c]=df[c].astype('category') if c in cats else pd.to_numeric(df[c])
    for mode in ['native_types','declared_types']:
        if mode=='declared_types':
            def guess(self,data):
                self._categorical_columns=[c for c in data if c in cats];self._numerical_columns=[c for c in data if c not in cats]
            ConformalAutoGluonCleaner._guess_dtypes=guess
        else:ConformalAutoGluonCleaner._guess_dtypes=original_guess
        np.random.seed(42)
        start=time.perf_counter();cleaner=ConformalAutoGluonCleaner(confidence_level=.95,seed=42)
        cleaner.fit(history.copy(),target_columns=targets,ci_calibration_size=.25,ci_ag_predictor_params={'path_prefix':str(R/'data/sota_followup/models'/('boundary_'+name+'_'+mode)),'verbosity':0},ci_ag_fit_params={'hyperparameters':{'RF':{'n_estimators':40},'XT':{'n_estimators':40}},'num_cpus':1,'time_limit':30,'hyperparameter_tune_kwargs':{'num_trials':1}})
        _,native,_=cleaner.remove_outliers(batch.copy(),empty_pred_sets_are_inliers=True);inclusive=native[targets].to_numpy(bool).copy();ties=np.zeros_like(inclusive);fields=[]
        for j,c in enumerate(targets):
            pred=cleaner.predictors_[c].predict(batch.copy(),sorted=True,allow_empty_set=True)
            if c in cleaner._numerical_columns:
                v=pd.to_numeric(batch[c]).to_numpy(float);boundary=(v==pred[:,0])|(v==pred[:,2]);closed=(v<pred[:,0])|(v>pred[:,2]);released=(v<=pred[:,0])|(v>=pred[:,2]);assert np.array_equal(released,native[c].to_numpy(bool));inclusive[:,j]=closed;ties[:,j]=boundary
                fields.append({'column':c,'native_type':'numeric','released_flags':int(released.sum()),'exact_endpoint_ties':int(boundary.sum()),'inclusive_interval_flags':int(closed.sum()),'zero_width_intervals':int((pred[:,0]==pred[:,2]).sum())})
            else:
                hist=history[c].astype(str).value_counts();rare=set(hist[hist<5].index);rarity=batch[c].astype(str).isin(rare).to_numpy();empty=np.array([np.count_nonzero(~pd.isna(row))==0 for row in pred]);fields.append({'column':c,'native_type':'categorical','released_flags':int(native[c].sum()),'empty_prediction_sets_treated_inlier':int(empty.sum()),'history_labels_with_fewer_than5_examples':len(rare),'alerts_on_these_labels':int((rarity&native[c].to_numpy(bool)).sum())})
        np.savez_compressed(O/(name+'_'+mode+'.npz'),released=native[targets].to_numpy(bool),inclusive=inclusive,endpoint_ties=ties)
        records.append({'dataset':name,'mode':mode,'fields':fields,'released_total':int(native[targets].to_numpy(bool).sum()),'inclusive_total':int(inclusive.sum()),'seconds':time.perf_counter()-start,'source_history_cleanliness':'UNKNOWN','adaptation':'inclusive endpoints is separate sensitivity; original code/primary predictions preserved'})
        original_main=np.load(R/f'results/sota_followup/ingest/{name}_full_untouched.npz')
        records[-1]['native_untouched_equals_primary']=bool(np.array_equal(native[targets].to_numpy(bool),original_main['cdc_original'])) if mode=='native_types' else None
        selected=O/'selected_cases';selected.mkdir(exist_ok=True)
        for path in sorted((R/'results/sota_followup/ingest').glob(name+'_*_ECAR_5_101_full.json')):
            d=json.loads(path.read_text());changed=batch.copy();logs=json.loads((R/d['log_path']).read_text())
            for e in logs:
                assert e['row_id'] in positions,'Source identity outside frozen evaluation population'
                changed.at[positions[e['row_id']],e['column']]=e['new']
            assert list(changed.index)==list(range(len(ids))) and len(changed)==800
            _,released,_=cleaner.remove_outliers(changed.copy(),empty_pred_sets_are_inliers=True);closed=released[targets].to_numpy(bool).copy()
            for j,c in enumerate(targets):
                if c not in cleaner._numerical_columns:continue
                pred=cleaner.predictors_[c].predict(changed.copy(),sorted=True,allow_empty_set=True);v=pd.to_numeric(changed[c]).to_numpy(float);closed[:,j]=(v<pred[:,0])|(v>pred[:,2])
            z=np.load(R/'results/sota_followup/ingest'/(d['scenario']+'.npz'));flags={k:z[k] for k in ['R','RS','RSM']};flags.update(cdc_released_diagnostic=released[targets].to_numpy(bool),cdc_inclusive_endpoints=closed);untouched={k:original_main[k] for k in ['R','RS','RSM']};untouched.update(cdc_released_diagnostic=native[targets].to_numpy(bool),cdc_inclusive_endpoints=inclusive)
            sid=d['scenario']+'_'+mode;np.savez_compressed(selected/(sid+'.npz'),truth=z['truth'],**flags);metrics=evaluate(flags,untouched,z['truth'],ids,targets)
            (selected/(sid+'.json')).write_text(json.dumps({'scenario':sid,'parent_case':d['scenario'],'dataset':name,'mode':mode,'family':d['family'],'selection':'All8 source-family cases, ECAR5%, seed101, full context; no favourable-outcome subset','metrics':metrics},separators=(',',':')))
        print(name,mode,records[-1]['released_total'],records[-1]['inclusive_total'],flush=True)
ConformalAutoGluonCleaner._guess_dtypes=original_guess
(O/'results.json').write_text(json.dumps(records,indent=2)+'\n')
