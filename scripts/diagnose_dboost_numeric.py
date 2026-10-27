import sys,json,subprocess,hashlib
from pathlib import Path
import numpy as np
from thesis_pilot.data import ROOT,load,SPECS
source=ROOT/'data/sources/cpitclaudel__dBoost';sys.path.insert(0,str(source))
from dboost.analyzers.utils import Stats
cases=[]
for value in [0.1,0.3,1.1,5191.0]:
 s=Stats()
 for _ in range(2400):s.update(value)
 try:out={'sigma':s.sigma,'state':'OK'}
 except Exception as e:out={'state':'FAILED','error':repr(e)}
 cases.append({'constant_value':value,'n':2400,'original':out,'independent_centered_sigma':float(np.sqrt(np.mean((np.full(2400,value)-value)**2)))})
parts,_=load('bank');spec=SPECS['bank'];history=parts['history'];batch=parts['evaluation'].iloc[:100]
commands=[]
for script in ['native_detector_worker.py','dboost_stable_compat.py']:
 fit={'op':'fit','method':'dboost_numeric_original','source':str(source),'columns':list(history),'targets':spec['targets'],'categorical':spec['categorical'],'rows':history.values.tolist()}
 score={'op':'score','method':'dboost_numeric_original','columns':list(batch),'rows':batch.values.tolist()}
 p=subprocess.run([str(ROOT/'data/envs/pilot/bin/python'),str(ROOT/'scripts'/script)],input=json.dumps(fit)+'\n'+json.dumps(score)+'\n',capture_output=True,text=True,timeout=120)
 responses=[]
 for line in p.stdout.splitlines():
  try:
   x=json.loads(line)
   if x.get('ok') and 'flags' in x['result']:
    flags=np.array(x['result']['flags'],bool);x={'ok':True,'shape':list(flags.shape),'alerts':int(flags.sum())}
   responses.append(x)
  except json.JSONDecodeError:pass
 commands.append({'script':script,'exit_code':p.returncode,'responses':responses,'stderr':p.stderr[-3000:]})
meta={'root_cause':'Original E[x^2]-E[x]^2 variance suffers catastrophic cancellation, potentially negative for constant float fields. Stable moments use population denominator n, independent centered variance agrees.','constant_tests':cases,'full_bank_probe':commands,'primary_effect':'Primary four-field Bank original fit succeeded; stable patch is a separately named diagnostic and not substituted into primary outcomes.'}
(ROOT/'evidence/thesis_pilot/dboost_numeric_diagnosis.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
