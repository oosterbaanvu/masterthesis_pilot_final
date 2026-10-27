"""Original pattern-only native one-outlier policy, matched to full benchmark reporting."""
import contextlib,io,json
from pathlib import Path
import pandas as pd
from thesis_pilot.data import ROOT
from sota_followup.benchmarks import AutoTestPattern,load_benchmark
O=ROOT/'results/sota_followup/values';O.mkdir(parents=True,exist_ok=True)
for name,corpus in [('rt','rt_train'),('st','st_train')]:
    rows,_=load_benchmark(name);model=AutoTestPattern(corpus);df=pd.DataFrame({'header':[r['header'] for r in rows],'dist_val':[r['values'] for r in rows]},index=[r['position'] for r in rows])
    with contextlib.redirect_stdout(io.StringIO()):
        matching=model.match_ns['get_matching_rows_pre_list'](df,[r[0] for r in model.rules]);parts=model.ns['pattern_check'](df,matching,model.rules)
    best={}
    for part in parts:
        for idx,row in part.iterrows():
            if idx not in best or row.conf<best[idx].conf:best[idx]=row
    lookup={r['position']:{v:i for i,v in enumerate(r['values'])} for r in rows};records=[{'column_position':int(idx),'value_position':lookup[idx][row.outlier],'confidence':1-float(row.conf)} for idx,row in best.items()]
    pd.DataFrame(records,columns=['column_position','value_position','confidence']).to_csv(O/(name+'_pattern_native.csv'),index=False);print(name,len(model.rules),'released pattern rules;',len(records),'native one-per-column alerts')
