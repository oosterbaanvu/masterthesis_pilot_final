"""Run unmodified algorithm statements from authors' two scripts on their Hospital.
Only the dataset-list assignment is parameterised through the AST; no algorithm branches changed.
No dummy labels are created: the authors' released GroundTruth file is used for their printed metrics.
"""
import ast,os,sys,json,runpy,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
r=Path(__file__).resolve().parents[1];source=r/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO';work=r/'data/lucario_authors_reproduction';work.mkdir(exist_ok=True)
if not (work/'datasets').exists():(work/'datasets').symlink_to(source/'datasets',target_is_directory=True)
for part in ['results/LUCARIO/constraints','results/LUCARIO/anomalies','results/GroundTruth']:(work/part).mkdir(parents=True,exist_ok=True)
for p in (source/'results/GroundTruth').glob('*'):
 target=work/'results/GroundTruth'/p.name
 if not target.exists():target.symlink_to(p)
sys.path.insert(0,str(source));os.chdir(work)
np.random.seed(42)
for file in ['constraint_inference.py','anomaly_detection.py']:
 tree=ast.parse((source/file).read_text())
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='datasets' for t in node.targets):node.value=ast.List(elts=[ast.Constant(value='hospital')],ctx=ast.Load())
 ast.fix_missing_locations(tree);exec(compile(tree,str(source/file),'exec'),{'__name__':'__main__'})
# Independent adapter parity using exactly the same dtype-reading as the authors.
sys.path.insert(0,str(r/'scripts'));from native_detector_worker import lucario_fit,lucario_score
# Importing worker must not enter its stdin loop; launch with empty input for this script.
df=pd.read_csv(source/'datasets/hospital/dirty.csv',keep_default_na=False,low_memory=False)
np.random.seed(42);cons=lucario_fit(df);actual=lucario_score(df,cons)
expected=pd.read_csv(work/'results/LUCARIO/anomalies/hospital_LUCARIO_detection.csv').to_numpy(bool)
meta={'source_revision':'3664bfa830b7b13f8a08cc7dd960c871c56aaeeb','dataset':'authors released Hospital','shape':list(actual.shape),'cell_flags_equal':bool(np.array_equal(actual,expected)),'disagreements':int((actual!=expected).sum()),'full_regex_inference_executed':True,'type_categorical_numeric_application_executed':True,'limitation':'single fixture parity, no universal fidelity or data rights assertion'}
(r/'evidence/thesis_pilot/lucario_authors_parity.json').write_text(json.dumps(meta,indent=2));print(meta);assert meta['cell_flags_equal']
