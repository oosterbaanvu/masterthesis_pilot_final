"""Predeclared hash-selected, label-free fresh feature comparisons against author caches."""
import hashlib,json,os,sys
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];S=R/'data/sota_followup/autotest37_source';os.chdir(S);sys.path.insert(0,str(S))
from util import sbert_utils,doduo_utils
records=[]
for name in ['rt','st']:
    rows=json.loads((R/('data/sota_followup/autotest_input_'+name+'.json')).read_text());selected=sorted(rows,key=lambda r:hashlib.sha256(('feature-audit|'+str(r['position'])).encode()).hexdigest())[:10];internal='labeled_benchmark' if name=='rt' else 'excel_benchmark'
    sb=pd.read_pickle(R/('data/sota_followup/autotest_storage/sbert_dist_embedding/'+internal+'_dist_val_embeddings.pkl'));do=pd.read_pickle(R/('data/sota_followup/autotest_storage/doduo/'+internal+'_dist_val_scores.pickle'))
    for row in selected:
        idx=row['position'];indices=sorted(set([0,len(row['values'])-1]))
        for i in indices:
            value=row['values'][i];fresh_sb=sbert_utils.decide_embedding(value);old_sb=sb.loc[idx][i] if hasattr(sb,'loc') else sb[idx][i];fresh_do=doduo_utils.predict([value])[0];old_do=do.loc[idx][0][i];sd=float(np.max(np.abs(np.asarray(fresh_sb)-np.asarray(old_sb))));dd=float(np.max(np.abs(np.asarray(fresh_do)-np.asarray(old_do))));records.append({'benchmark':name,'column_position':idx,'value_position':i,'sbert_max_abs_difference':sd,'doduo_max_abs_difference':dd,'sbert_atol_1e5':sd<1e-5,'doduo_atol_1e4':dd<1e-4})
        print(name,idx,'fresh cache comparison complete',flush=True)
result={'status':'PASSED' if all(r['sbert_atol_1e5'] and r['doduo_atol_1e4'] for r in records) else 'DIFFERENCES_FOUND','sampling':'10 columns/benchmark chosen by fixed SHA256(feature-audit|position), first/last values; no labels used','comparisons':records,'labels_consumed':0,'scope':'Deterministic probe and full cache cardinality checks, not proof that every published feature was freshly reproduced'};(R/'evidence/sota_followup/cache_integrity_extended.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(records),'value feature pairs')
