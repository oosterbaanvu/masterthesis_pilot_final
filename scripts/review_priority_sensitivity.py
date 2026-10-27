"""Re-score cached predictions with provenance priority, without any new model fit.
No truth array is read until the review schedule has been formed from control flags.
"""
import hashlib,itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'results/thesis_pilot';out=[]
def ordered(flags,ids,cols):return sorted(map(tuple,np.argwhere(flags)),key=lambda p:hashlib.sha256((ids[p[0]]+'|'+cols[p[1]]).encode()).digest())
for file in sorted((O/'scenarios').glob('*.json')):
 d=json.loads(file.read_text());pop=json.loads((O/(d['dataset']+'_population.json')).read_text());ids=pop['parts']['evaluation'];cols=pop['evaluated_targets'];z=np.load(O/'predictions'/(d['scenario']+'.npz'));hard=ordered(z['A'],ids,cols);stats=ordered(z['B']&~z['A'],ids,cols)
 for method in z.files:
  if method in ['A','B','truth']:continue
  detector=ordered(z[method]&~z['A'],ids,cols)
  for budget in [10,25,50]:
   k=int(np.ceil(len(ids)*budget/1000));base=set((hard+stats)[:k])
   for policy in ['control_first','equal_share']:
    if policy=='control_first':seq=hard+stats+detector
    else:seq=hard+[x for pair in itertools.zip_longest(stats,detector) for x in pair if x is not None]
    selected=set(list(dict.fromkeys(seq))[:k]);truth=set(map(tuple,np.argwhere(z['truth'])))
    out.append({'scenario':d['scenario'],'dataset':d['dataset'],'family':d['family'],'mechanism':d['mechanism'],'rate':d['rate'],'seed':d['seed'],'method':method,'policy':policy,'budget_per_1000':budget,'unit':'cell review','hard_alerts':len(hard),'reviewed':len(selected),'changed_cells':len(truth),'hits':len(selected&truth),'baseline_hits':len(base&truth),'net_hits':len(selected&truth)-len(base&truth),'lost_baseline_hits':len((base-selected)&truth),'net_recall':(len(selected&truth)-len(base&truth))/len(truth),'labels_used_for_ordering':False})
df=pd.DataFrame(out);df.to_csv(O/'hard_priority_budget_results.csv',index=False)
keys=['dataset','family','mechanism','rate','method','policy','budget_per_1000'];df.groupby(keys).agg(scenarios=('scenario','nunique'),mean_net_hits=('net_hits','mean'),mean_net_recall=('net_recall','mean'),mean_lost_hits=('lost_baseline_hits','mean')).reset_index().to_csv(O/'hard_priority_budget_summary.csv',index=False)
print('Re-scored',len(out),'budget comparisons using source-contract provenance; no model retraining or label-based priority.')
