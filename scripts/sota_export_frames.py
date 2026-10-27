"""Canonical split identities are resolved only in the pinned main environment."""
import hashlib,json
from pathlib import Path
import pandas as pd
from thesis_pilot.data import ROOT,load,SPECS
records=[]
for name in ['credit','bank','wine']:
    parts,meta=load(name);canonical=json.loads((ROOT/f'results/sota_followup/ingest/{name}_full_population.json').read_text());assert meta['parts']==canonical['parts']
    d={'dataset':name,'main_pandas':pd.__version__,'source_sha256':meta['source_sha256'],'columns':list(parts['history']),'targets':SPECS[name]['targets'],'categories':SPECS[name]['categorical'],'history_ids':list(parts['history'].index),'evaluation_ids':list(parts['evaluation'].index),'history_values':parts['history'].values.tolist(),'evaluation_values':parts['evaluation'].values.tolist()};p=ROOT/f'data/sota_followup/{name}_canonical_frames.json';p.write_text(json.dumps(d));records.append({'dataset':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_sha256':meta['source_sha256'],'history_rows':len(d['history_ids']),'evaluation_rows':len(d['evaluation_ids']),'main_pandas':pd.__version__,'labels':'No error labels or outcome fields; immutable source IDs kept outside model arrays'})
(ROOT/'manifests/sota_followup/canonical_runtime_bridge.json').write_text(json.dumps(records,indent=2)+'\n')
