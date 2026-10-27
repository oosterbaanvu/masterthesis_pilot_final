"""Original Raha learning pipeline with explicit, metered publisher-label oracle.
No clean_path is supplied; only 20 sampled row label vectors reach the method.
KBVD disabled through its published configurable strategy list (reported ablation).
"""
import os,sys,json,time,random
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];source=Path('/workspace/research_sources/BigDaMa__raha');sys.path.insert(0,str(source))
import raha
random.seed(42);np.random.seed(42);start=time.perf_counter()
base=ROOT/'data/raw/BigDaMa__raha/datasets/hospital';work=ROOT/'data/raha_external';work.mkdir(exist_ok=True)
dirty=pd.read_csv(base/'dirty.csv',dtype=str,keep_default_na=False).drop(columns=['index'])
clean=pd.read_csv(base/'clean.csv',dtype=str,keep_default_na=False).drop(columns=['index']);clean.columns=dirty.columns
dirty.to_csv(work/'dirty.csv',index=False)
# Label oracle uses the method's published representation normalizer, not final-label tuning.
reference=clean.map(raha.Dataset.value_normalizer);dirty_normalized=dirty.map(raha.Dataset.value_normalizer);truth=dirty_normalized.to_numpy()!=reference.to_numpy()
app=raha.Detection();app.SAVE_RESULTS=False;app.VERBOSE=False;app.LABELING_BUDGET=20;app.ERROR_DETECTION_ALGORITHMS=['OD','PVD','RVD'];app.STRATEGY_FILTERING=False
d=app.initialize_dataset({'name':'hospital_metered','path':str(work/'dirty.csv')});d.has_ground_truth=False
# Any algorithmic attempt to retrieve all labels fails. Oracle code below is outside the detector.
def no_oracle_access():raise RuntimeError('Forbidden bulk reference access')
d.get_actual_errors_dictionary=no_oracle_access
# Bound worker process creation to available CPUs; no algorithm or parameter change.
import multiprocessing
original_pool=multiprocessing.Pool
multiprocessing.Pool=lambda *a,**kw:original_pool(processes=2)
app.run_strategies(d);app.generate_features(d);app.build_clusters(d)
assert not hasattr(d,'clean_dataframe')
queries=[]
while len(d.labeled_tuples)<app.LABELING_BUDGET:
 app.sample_tuple(d);i=int(d.sampled_tuple);queries.append(i);d.labeled_tuples[i]=1
 for j in range(d.dataframe.shape[1]):d.labeled_cells[(i,j)]=[int(truth[i,j]),None]
app.propagate_labels(d);app.predict_labels(d)
flag=np.zeros(truth.shape,bool)
for i,j in d.detected_cells:flag[i,j]=True
eligible=np.ones(truth.shape,bool);eligible[queries,:]=False
# Labeled answers are excluded from assessment; label review cost is reported separately.
hits=int((flag&truth&eligible).sum());alerts=int((flag&eligible).sum());positive=int((truth&eligible).sum())
out=ROOT/'results/thesis_pilot/external';out.mkdir(exist_ok=True)
np.savez_compressed(out/'hospital_raha_few_label.npz',flags=flag,truth=truth,eligible=eligible)
meta={'method':'Raha original OD/PVD/RVD (KBVD disabled ablation)','source_revision':'7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c','status':'EXECUTED_CONDITIONAL','dataset':'Hospital','information_regime':'20 metered publisher-reference labelled rows; no clean reference features, labels excluded from scored rows','queried_row_positions':queries,'annotation_rows':len(queries),'annotation_cells':len(queries)*truth.shape[1],'reference_hits':hits,'alerts':alerts,'positives':positive,'reference_precision':hits/alerts if alerts else None,'reference_recall':hits/positive if positive else None,'seconds':time.perf_counter()-start,'strategy_count':len(d.strategy_profiles),'label_semantics':'published normalized reference differences, not independently verified natural semantic errors'}
(out/'hospital_raha_few_label.json').write_text(json.dumps(meta,indent=2));print(meta)
