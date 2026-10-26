"""Second counting implementation. Deliberately does not import thesis_audit."""
import ast,collections,csv,hashlib,json,pathlib
root=pathlib.Path('.');checks=[]
def check(name,condition,details=None):
 checks.append({'check':name,'status':'PASSED' if condition else 'FAILED','details':details})
 if not condition:raise AssertionError(name)
files=json.loads((root/'manifests/files.json').read_text())
for x in files:
 b=(root/x['path']).read_bytes();check('integrity:'+x['path'],len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'])
for a in json.loads((root/'evidence/pair_audits.json').read_text()):
 name=a['name']
 if name.startswith('raha_'):
  p=root/'data/raw/BigDaMa__raha/datasets'/name.removeprefix('raha_');dirty=p/'dirty.csv';clean=p/'clean.csv'
 else:
  p=root/'data/raw/calgo-lab__error-paper/data'/name;dirty=p/(name+'_3_1.csv');clean=p/'clean.csv'
 with dirty.open(newline='',encoding='utf-8-sig') as f:dr=list(csv.reader(f))[1:]
 with clean.open(newline='',encoding='utf-8-sig') as f:cr=list(csv.reader(f))[1:]
 diffs=sum(sum(x!=y for x,y in zip(d,c)) for d,c in zip(dr,cr))
 check('raw_difference_recount:'+name,diffs==a['raw_differences'])
 check('label_conservation:'+name,sum(a['counts'].values())==len(dr)*len(dr[0]))
 with (root/'data/derived'/(name+'_labels.csv')).open(newline='') as f:labels=list(csv.DictReader(f))
 counts=collections.Counter(x['status'] for x in labels)
 check('label_artifact_recount:'+name,len(labels)==diffs and all(counts[s]==n for s,n in a['counts'].items() if s!='NOT_AN_ERROR'))
 check('no_unearned_semantic_certification:'+name,a['counts'].get('VERIFIED_REFERENCE_ERROR',0)==0)
 # Independently check every saved audit original/reference against bytes, not only aggregate counts.
 for x in json.loads((root/'data/derived'/(name+'_sample.json')).read_text()):
  with dirty.open(newline='',encoding='utf-8-sig') as f:h=next(csv.reader(f))
  j=h.index(x['column']);i=x['row'];assert (x['original'],x['reference'])==(dr[i][j],cr[i][j])
 check('audit_sample_coordinates:'+name,True)
for a in json.loads((root/'evidence/column_audits.json').read_text()):
 p=root/'data/raw/qixuchen__AutoTest/benchmarks'/(a['name']+'.csv');physical=empty=valid=positives=debates=values=0
 rejected=[]
 with p.open(encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):
   physical+=1
   if not any(row.values()):empty+=1;continue
   try:
    lists=[ast.literal_eval(row[k]) for k in ['dist_val','ground_truth','ground_truth_debatable']]
    assert all(type(v)==list and all(type(x)==str for x in v) for v in lists)
    v,g,b=lists;assert len(v)==len(set(v))==int(row['dist_val_count']);assert set(g+b).issubset(v);assert not(set(g)&set(b))
   except (AssertionError,SyntaxError,ValueError):rejected.append(row['index']);continue
   valid+=1;positives+=len(g);debates+=len(b);values+=len(v)
 c=a['counts'];check('independent_column_recount:'+a['name'],(physical,empty,valid,positives,debates,values)==(c['physical_records'],c.get('fully_empty_records',0),c['eligible_columns'],c['published_positive'],c['published_debatable'],c['eligible_values']))
 check('exact_exclusions:'+a['name'],set(rejected)=={x['index'] for x in a['issues']})
cols=json.loads((root/'evidence/column_audits.json').read_text());inter=set(cols[0]['column_fingerprints'])&set(cols[1]['column_fingerprints'])
checks.append({'check':'cross_benchmark_exact_header_value_overlap','status':'OBSERVED','details':len(inter),'limitation':'Cannot check table identity or hidden training corpora using these fingerprints'})
# Machine-readable gate and matrix validation, independently of protocol helpers.
qualification=json.loads((root/'manifests/qualification.json').read_text())
check('no_unqualified_primary_admission',not any(x.get('primary_accepted') for x in qualification))
matrix=json.loads((root/'manifests/compatibility.json').read_text())
check('matrix_complete',len(matrix)==len(qualification)*5)
check('no_multicolumn_on_invented_rt_st_rows',all(x['status']=='INCOMPATIBLE' for x in matrix if x['dataset'] in {'rt_bench','st_bench'} and x['method'] in {'cdc','dboost','raha','isolation_forest'}))
protocol=json.loads((root/'configs/protocol_v0.1.json').read_text())
check('experiment_hard_gate_closed',protocol['execution_allowed'] is False and protocol['primary_datasets']==[])
for a in cols:
 values=[str(a['counts'][k]) for k in ['eligible_columns','eligible_values','published_positive']]
 text=(root/'reports/02_ground_truth_audit.md').read_text()
 check('report_numbers:'+a['name'],all(v in text for v in values))
(root/'evidence/independent_checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({'passed':sum(x['status']=='PASSED' for x in checks),'failed':sum(x['status']=='FAILED' for x in checks),'cross_benchmark_overlap':len(inter)}))
