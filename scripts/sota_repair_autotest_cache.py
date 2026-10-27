"""Recompute only structurally mismatched feature entries, using original label-free helpers."""
import hashlib,json,os,sys
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];S=R/'data/sota_followup/autotest37_source';os.chdir(S);sys.path.insert(0,str(S));from util import sbert_utils,doduo_utils
records=[]
for name,internal in [('rt','labeled_benchmark'),('st','excel_benchmark')]:
 rows=json.loads((R/f'data/sota_followup/autotest_input_{name}.json').read_text())
 for kind,folder,suffix,extension in [('sbert','sbert_dist_embedding','dist_val_embeddings','pkl'),('doduo','doduo','dist_val_scores','pickle')]:
  original=S/f'demo/cache/{name}_bench_{suffix}.{extension}';published=pd.read_pickle(original);local=R/f'data/sota_followup/{name}_{kind}_cache_input_repaired.pkl';cache=pd.read_pickle(local) if local.exists() else published.copy();changed=[]
  for row in rows:
   idx=row['position'];values=row['values'];entry=cache.loc[idx];length=len(entry[0]) if kind=='doduo' else len(entry)
   if length==len(values):continue
   if name!='st' or idx!=858:raise ValueError('Unexpected new structural mismatch: version and audit before repair')
   if kind=='sbert':fresh=sbert_utils.dist_val_embeddings(values)
   else:
    frame=pd.DataFrame({'dist_val':[[v] for v in values]});fresh=doduo_utils.predict_multi_row(frame);pd.to_pickle(fresh,R/'data/sota_followup/st858_doduo_fresh.pkl')
   cache.values[cache.index.get_loc(idx)]=fresh;changed.append(idx)
  mismatch=[r['position'] for r in rows if (len(cache.loc[r['position']][0]) if kind=='doduo' else len(cache.loc[r['position']]))!=len(r['values'])];assert not mismatch
  if changed:cache.to_pickle(local)
  target=R/f'data/sota_followup/autotest_storage/{folder}/{internal}_{suffix}.{extension}';desired=local if local.exists() else original
  if target.is_symlink() and target.resolve()!=desired.resolve():target.unlink()
  if not target.exists():target.symlink_to(desired)
  records.append({'benchmark':name,'feature':kind,'fresh_columns_this_invocation':changed,'all_selected_cardinalities_match':True,'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'effective_sha256':hashlib.sha256(desired.read_bytes()).hexdigest(),'labels_used':0})
(R/'evidence/sota_followup/cache_setup_replay.json').write_text(json.dumps({'status':'PASSED','checks':records,'scope':'Reuse pinned original feature caches with one exact-input structural preprocessing repair; no all-feature-fresh claim'},indent=2)+'\n');print('All eligible cached feature entries aligned')
