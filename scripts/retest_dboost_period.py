"""Concrete Bank-period floating-point failure and stable-moment retest, using history only."""
import sys,json,subprocess
import numpy as np
from thesis_pilot.data import ROOT,load,SPECS
parts,_=load('bank');h=parts['history'];df=h[h['emp.var.rate']==-3.4].iloc[:20].copy();assert len(df)==20
rows=[]
for script in ['native_detector_worker.py','dboost_stable_compat.py']:
 fit={'op':'fit','method':'dboost_numeric_original','source':str(ROOT/'data/sources/cpitclaudel__dBoost'),'columns':list(df),'targets':SPECS['bank']['targets'],'categorical':SPECS['bank']['categorical'],'rows':df.values.tolist()}
 score={'op':'score','method':'dboost_numeric_original','columns':list(df),'rows':df.values.tolist()}
 p=subprocess.run([str(ROOT/'data/envs/pilot/bin/python'),str(ROOT/'scripts'/script)],input=json.dumps(fit)+'\n'+json.dumps(score)+'\n',capture_output=True,text=True,timeout=60)
 responses=[]
 for line in p.stdout.splitlines():
  q=json.loads(line)
  if q.get('ok') and 'flags' in q['result']:
   f=np.array(q['result']['flags'],bool);q={'ok':True,'shape':list(f.shape),'alerts':int(f.sum())}
  responses.append(q)
 rows.append({'script':script,'exit_code':p.returncode,'responses':responses,'stderr':p.stderr[-2500:]})
require_failure=not rows[0]['responses'][0]['ok'];require_success=all(x['ok'] for x in rows[1]['responses']);assert require_failure and require_success
out={'dataset':'Bank Marketing','population':'20 approved historical rows with emp.var.rate=-3.4, all 20 non-outcome input features','source_row_ids':list(df.index),'original_failure_reproduced':require_failure,'repaired_full_population_score_succeeded':require_success,'root_cause':'Native float fractional-part expansion produces a constant approximately -0.4; one-pass variance becomes slightly negative through cancellation. Cached stable population moments avoid this without clipping variances or dropping inputs.','results':rows,'primary_results_changed':False}
(ROOT/'evidence/thesis_pilot/dboost_period_retest.json').write_text(json.dumps(out,indent=2));print(out)
