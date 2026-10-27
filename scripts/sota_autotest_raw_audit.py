"""Independent legacy-pickle to coordinate export parity, without production helpers."""
import csv,json
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];checks=[]
for name,corpus in [('rt','rt_train'),('st','st_train')]:
 source=json.loads((R/f'data/sota_followup/autotest_input_{name}.json').read_text());lookup={r['position']:r['values'] for r in source};raw=pd.read_pickle(R/f'data/sota_followup/autotest_runs/{name}_{corpus}_raw_native_result.pkl');actual=[]
 for idx,row in raw.iterrows():
  hits=[i for i,v in enumerate(lookup[idx]) if v==row['outlier']];assert len(hits)==1;actual.append((int(idx),hits[0],float(row['conf'])))
 with (R/f'results/sota_followup/values/{name}_{corpus}_autotest_full.csv').open() as f:expected=[(int(x['column_position']),int(x['value_position']),float(x['confidence'])) for x in csv.DictReader(f)]
 assert len(actual)==len(expected) and all(a[:2]==b[:2] and abs(a[2]-b[2])<1e-12 for a,b in zip(actual,expected));checks.append({'benchmark':name,'native_outliers':len(actual),'coordinate_disagreements':0})
(R/'evidence/sota_followup/autotest_raw_coordinate_audit.json').write_text(json.dumps({'status':'PASSED','checks':checks,'scope':'Independent mapping of original raw outputs to distinct value coordinates; not semantic adjudication'},indent=2)+'\n');print(checks)
