"""Retain full native learned constraints locally; commit only summaries/checksums.
This prevents external benchmark values embedded in inferred category domains from
being redistributed as if they were harmless configuration metadata.
"""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];out=R/'data/pilot_models/native_constraint_outputs';out.mkdir(parents=True,exist_ok=True)
for path in (R/'evidence/thesis_pilot').glob('*lucario*_fit.json'):
 data=json.loads(path.read_text())
 if 'constraints' not in data:continue
 original=path.read_bytes();local=out/path.name;local.write_bytes(original);cons=data.pop('constraints')
 data['native_constraint_output_path']=str(local.relative_to(R));data['native_constraint_sha256']=hashlib.sha256(original).hexdigest()
 data['constraints_summary']={c:{'type':v.get('type_constraint'),'category_count':len(v['categorical_constraint']) if v.get('categorical_constraint') is not None else None,'pattern_count':len(v.get('pattern_constraint',[])),'numerical_constraint_present':v.get('numerical_constraint') is not None} for c,v in cons.items()}
 data['retention']='Full native output kept in ignored data; original-source code/model values are not redistributed.'
 path.write_text(json.dumps(data,indent=2)+'\n')
print('Native constraints retained locally; metadata sanitized.')
