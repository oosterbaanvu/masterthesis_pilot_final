"""Original author statements versus reusable adapter, with declared deterministic seeds."""
import ast,hashlib,json,os,sys
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];S=R/'data/sources/RIOLU';W=R/'data/sota_followup/riolu_parity';W.mkdir(exist_ok=True)
for name in ['test_anomaly_detection','ground_truth_anomaly_detection']:
    if not (W/name).exists():(W/name).symlink_to(S/name,target_is_directory=True)
(W/'results/auto_riolu').mkdir(parents=True,exist_ok=True)
tree=ast.parse((S/'Auto-RIOLU.py').read_text())
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='dataset' for t in node.targets):node.value=ast.Constant(value='hosp_1k')
    if isinstance(node,ast.For) and isinstance(node.target,ast.Name) and node.target.id=='column':node.body.insert(0,ast.parse('np.random.seed(42)').body[0])
ast.fix_missing_locations(tree);sys.path.insert(0,str(S));os.chdir(W);exec(compile(tree,str(S/'Auto-RIOLU.py'),'exec'),{'__name__':'__main__'})
expected=pd.read_csv(W/'results/auto_riolu/auto_riolu_hosp_1k.csv',index_col=0);dirty=pd.read_csv(S/'test_anomaly_detection/hosp_1k/dirty_hosp_1k.csv',dtype=str)
sys.path.insert(0,str(R/'src'));from sota_followup.pattern_adapter import BoundedPatternWorker
worker=BoundedPatternWorker();actual=[]
try:
    for column in expected:actual.append(worker.score([None if pd.isna(v) else str(v) for v in dirty[column]])['flags'])
finally:worker.close()
actual=np.asarray(actual,bool).T;known=expected.to_numpy()>=0;mismatch=int(((actual!=(expected.to_numpy()==1))&known).sum());out=R/'results/sota_followup/riolu_authors_parity.npz';np.savez_compressed(out,author_flags=expected.to_numpy(),adapter_flags=actual,comparable=known)
result={'status':'PASSED' if mismatch==0 else 'FAILED','source_revision':'df3f7dc7673fda3f02d147fdf4c539a2bf3cc4d5','fixture':'authors modified Hospital1k','shape':list(actual.shape),'compared_nonmissing_flags':int(known.sum()),'native_missing_abstentions':int((~known).sum()),'disagreements':mismatch,'harness_changes':['select hosp_1k fixture','explicit NumPy seed42 per column; Python hashseed0'],'oracle_column_selection':'Original authors harness selects columns from ground-truth header. Used only for fidelity fixture, never new comparison column selection.','flag_file_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'scope':'one fixture application parity, not paper-score reproduction or new independent dataset'};(R/'evidence/sota_followup/riolu_authors_parity.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert mismatch==0
