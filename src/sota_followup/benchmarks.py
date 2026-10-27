"""Publisher-labelled distinct values, with no invented relational rows."""
import ast,collections,csv,hashlib,json,types,contextlib,io
from pathlib import Path
import numpy as np
import pandas as pd
from thesis_pilot.data import ROOT

def load_benchmark(name):
    path=ROOT/f'data/raw/qixuchen__AutoTest/benchmarks/{name}_bench.csv';rows=[];excluded=[];seen=set();counts=collections.Counter()
    with path.open(encoding='utf-8-sig',newline='') as f:
        for position,row in enumerate(csv.DictReader(f)):
            counts['physical_records']+=1
            if all(v=='' for v in row.values()):counts['fully_empty']+=1;continue
            errors=[];rid=row['index']
            if rid in seen:errors.append('DUPLICATE_INDEX')
            seen.add(rid)
            try:
                values,positive,ambiguous=[ast.literal_eval(row[k]) for k in ['dist_val','ground_truth','ground_truth_debatable']]
                if not all(isinstance(x,list) and all(isinstance(v,str) for v in x) for x in [values,positive,ambiguous]):raise ValueError('Not string lists')
                if len(values)!=len(set(values)):errors.append('DUPLICATE_DISTINCT_VALUE')
                if len(values)!=int(row['dist_val_count']):errors.append('COUNT_MISMATCH')
                if not set(positive+ambiguous)<=set(values):errors.append('LABEL_OUTSIDE_UNIVERSE')
                if set(positive)&set(ambiguous):errors.append('CONTRADICTORY_LABEL')
            except Exception as e:errors.append(type(e).__name__)
            if errors:excluded.append({'position':position,'id':rid,'issues':errors});continue
            rows.append({'position':position,'id':rid,'header':row['header'],'values':values,'positive':positive,'ambiguous':ambiguous})
            counts['eligible_columns']+=1;counts['distinct_values']+=len(values);counts['positives']+=len(positive);counts['ambiguous']+=len(ambiguous)
    inventory={'benchmark':name,'counts':dict(counts),'excluded':excluded,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'unit':'distinct value within published column','truth':'C_PUBLISHER_REFERENCE','source_table_and_occurrence_frequencies':'NOT_PROVIDED','semantic_adjudication':'NOT_INDEPENDENTLY_VERIFIED'}
    return rows,inventory

def statistical_flags(values):
    """Fixed label-free dirty-column heuristic; no authoritative schema is invented."""
    s=pd.Series(values,dtype=str);n=pd.to_numeric(s,errors='coerce');flags=np.zeros(len(s),bool)
    if n.notna().mean()>=.95:
        flags |= n.isna().to_numpy();good=n.dropna()
        if len(good)>3:
            q=good.quantile([.005,.25,.75,.995]).to_numpy();iqr=q[2]-q[1]
            flags |= ((n<q[0])|(n>q[3])|(n<q[1]-3*iqr)|(n>q[2]+3*iqr)).to_numpy()
    else:
        # Coarse character-category/length profiling is explicitly a heuristic.
        import re
        shape=s.map(lambda v:re.sub(r'[A-Za-z]+','A',re.sub(r'\d+','9',v)))
        shares=shape.map(shape.value_counts(normalize=True));flags|=(shares.to_numpy()<.005)
    return flags

class AutoTestPattern:
    """Original published pattern-family online functions; explicit restricted ablation."""
    def __init__(self,corpus='rt_train'):
        root=Path('/workspace/research_sources/qixuchen__AutoTest/code/AutoTest')
        table=pd.read_csv(root/f'results/SDC/{corpus}_selected_sdc.csv',sep='\t')
        all_rules=[ast.literal_eval(v) for v in table.SDC]
        self.rules=[v for v in all_rules if v[0][0]=='pattern' and v[1][0]=='pattern'];self.corpus=corpus
        fn=next(n for n in ast.parse((root/'util/utils.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='get_matching_rows_from_idx_dict')
        ns={};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(root/'util/utils.py'),'exec'),ns)
        self.ns={'pd':pd,'np':np,'re':__import__('regex'),'utils':types.SimpleNamespace(get_matching_rows_from_idx_dict=ns[fn.name])}
        tree=ast.parse((root/'check/pattern_check.py').read_text());body=[n for n in tree.body if isinstance(n,ast.FunctionDef)]
        exec(compile(ast.Module(body=body,type_ignores=[]),str(root/'check/pattern_check.py'),'exec'),self.ns)
        import re
        self.match_ns={'pd':pd,'np':np,'re':re}
        body=[n for n in ast.parse((root/'util/pattern_utils.py').read_text()).body if isinstance(n,ast.FunctionDef)]
        exec(compile(ast.Module(body=body,type_ignores=[]),str(root/'util/pattern_utils.py'),'exec'),self.match_ns)
    def score_columns(self,rows):
        df=pd.DataFrame({'header':[r['header'] for r in rows],'dist_val':[r['values'] for r in rows]},index=[r['position'] for r in rows])
        # Only label-free published inputs reach native precondition/application functions.
        with contextlib.redirect_stdout(io.StringIO()):
            matching=self.match_ns['get_matching_rows_pre_list'](df,[r[0] for r in self.rules])
            results=self.ns['pattern_all_outliers'](df,matching,self.rules)
        outputs={r['position']:np.zeros(len(r['values']),bool) for r in rows};scores={r['position']:np.zeros(len(r['values'])) for r in rows};lookup={}
        for row in rows:
            positions=collections.defaultdict(list)
            for i,v in enumerate(row['values']):positions[v].append(i)
            lookup[row['position']]=positions
        for result in results:
            for idx,row in result.iterrows():
                for val in row.outlier:
                    for pos in lookup[idx][val]:outputs[idx][pos]=True;scores[idx][pos]=max(scores[idx][pos],1-float(row.conf))
        return outputs,scores
