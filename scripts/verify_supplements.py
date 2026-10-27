"""Independent arithmetic/identity checks for external, row and scope supplements."""
import collections,hashlib,html,io,itertools,json,re,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'results/thesis_pilot';checks=collections.Counter()
def require(ok,kind):
 if not ok:raise AssertionError(kind)
 checks[kind]+=1

def order(f,ids,cols):return sorted(map(tuple,np.argwhere(f)),key=lambda x:hashlib.sha256(f'{ids[x[0]]}|{cols[x[1]]}'.encode()).digest())
def selection(b,d,k,policy):
 seq=b+d if policy=='control_first' else [x for pair in itertools.zip_longest(b,d) for x in pair if x is not None]
 return set(list(dict.fromkeys(seq))[:k])

def verify_metrics(meta,z,original,ids,targets):
 t=set(map(tuple,np.argwhere(z['truth'])))
 for m in meta['metrics']:
  base=m['baseline'];method=m['method'];b=set(map(tuple,np.argwhere(z[base])));d=set(map(tuple,np.argwhere(z[method])))
  if m['mode']=='budget_union':
   k=int(np.ceil(m['budget_per_1000']*len(ids)/1000));selected=selection(order(z[base],ids,targets),order(z[method],ids,targets),k,m['policy']);bs=set(order(z[base],ids,targets)[:k])
   require(m['hits']==len(selected&t) and m['reviewed']==len(selected)<=k,'supplement_budget_hits')
   require(m['net_hits']==len(selected&t)-len(bs&t),'supplement_budget_net')
  else:
   f=d if m['mode']=='alone' else b|d;require(m['hits']==len(f&t) and m['alerts']==len(f),'supplement_flag_metrics')
   require(m['additional_hits']==len((f-b)&t) and m['additional_alerts']==len(f-b),'supplement_incremental_metrics')

for folder in ['full_feature_probe','cdc_type_diagnostic']:
 path=O/folder/'results.json'
 if not path.exists():continue
 records=json.loads(path.read_text());require(len(records)==18,folder+'_scenario_count')
 for meta in records:
  sid=meta['scenario'];z=np.load(O/folder/(sid+'.npz'));primary=np.load(O/'predictions'/(sid+'_5_101.npz'))
  require(np.array_equal(z['truth'],primary['truth']),folder+'_same_target_population_and_changes')
  pop=json.loads((O/(meta['dataset']+'_population.json')).read_text());ids=pop['parts']['evaluation'];cols=pop['evaluated_targets']
  # The original prediction sets are not needed for independent basic/union/budget arithmetic.
  verify_metrics(meta,z,None,ids,cols)

# External track: independently reopen raw references; exact field correspondence is explicit.
for name in ['hospital','beers']:
 z=np.load(O/'external'/(name+'.npz'));meta=json.loads((O/'external'/(name+'.json')).read_text());base=R/'data/raw/BigDaMa__raha/datasets'/name
 d=pd.read_csv(base/'dirty.csv',dtype=str,keep_default_na=False);c=pd.read_csv(base/'clean.csv',dtype=str,keep_default_na=False);c.columns=d.columns
 drop=[x for x in ['index','id'] if x in d];d=d.drop(columns=drop);c=c.drop(columns=drop);truth=d.to_numpy()!=c.to_numpy()
 require(np.array_equal(truth,z['truth']),'external_raw_reference_alignment')
 for row in meta['outcomes']:
  b=z[row['baseline']];f=z[row['method']];extra=f&~b
  require(row['reference_hits']==int((f&truth).sum()) and row['alerts']==int(f.sum()),'external_reference_counts')
  require(row['additional_reference_hits']==int((extra&truth).sum()) and row['additional_alerts']==int(extra.sum()),'external_incremental_counts')

q=json.loads((O/'external/hospital_raha_few_label.json').read_text());z=np.load(O/'external/hospital_raha_few_label.npz');ids=q['queried_row_positions'];require(len(ids)==len(set(ids))==20,'raha_metered_label_budget')
expected=np.ones_like(z['eligible']);expected[ids,:]=False;require(np.array_equal(expected,z['eligible']),'raha_labels_excluded_from_evaluation')
require(q['reference_hits']==int((z['flags']&z['truth']&z['eligible']).sum()),'raha_reference_recount');require(q['annotation_cells']==20*z['truth'].shape[1],'raha_feedback_cost')

# All matched source/family/seed/row transformations remain identical across mechanisms and rates.
values={};counts={}
for p in sorted((O/'scenarios').glob('*.json')):
 meta=json.loads(p.read_text());logs=json.loads((R/meta['injection_log']).read_text());key=(meta['dataset'],meta['family'],meta['rate'],meta['seed']);n=len(logs)
 if key in counts:require(counts[key]==n,'matched_mechanism_change_counts')
 counts[key]=n
 for e in logs:
  key=(meta['dataset'],meta['family'],meta['seed'],e['source_row_id'])
  if key in values:require(values[key]==(e['original'],e['new']),'identical_per_row_transformation_across_mechanisms')
  values[key]=(e['original'],e['new'])

# Row-level E6 source reconstruction uses original approved source rows and the actual intervention,
# and verifies the independently stipulated row relation instead of assigning blame to both cells.
row_path=O/'bank_crossfield_rows/results.json'
if row_path.exists():
 records=json.loads(row_path.read_text());require(len(records)==45,'row_crossfield_scenario_count')
 with zipfile.ZipFile(R/'data/recovery_downloads/bank+marketing.zip') as z:
  with zipfile.ZipFile(io.BytesIO(z.read('bank-additional.zip'))) as zz:bank=pd.read_csv(io.BytesIO(zz.read('bank-additional/bank-additional-full.csv')),sep=';').drop(columns='y')
 bank.index=[f'bank:{i}' for i in range(len(bank))];pop=json.loads((O/'bank_population.json').read_text());bank=bank.loc[pop['parts']['evaluation']]
 eligible=bank[(bank.previous>0)&bank.poutcome.isin(['failure','success'])]
 for meta in records:
  z=np.load(O/'bank_crossfield_rows'/(meta['scenario']+'.npz'));changed=bank.copy();changed.loc[meta['changed_row_ids'],'previous']=0
  relation=(changed.previous==0)!=(changed.poutcome=='nonexistent');require(np.array_equal(relation.to_numpy()[:,None],z['truth']),'row_contract_not_cell_blame')
  require(len(meta['changed_row_ids'])==meta['realized_count']==max(1,int(len(eligible)*meta['rate'])),'row_realized_counts')
  rng=np.random.default_rng(meta['seed']);n=meta['realized_count']
  if meta['mechanism']=='ECAR':selected=rng.choice(eligible.index,n,replace=False)
  else:
   column='age' if meta['mechanism']=='EAR' else 'previous';start=int(rng.integers(0,len(eligible)-n)) if len(eligible)>n else 0;selected=eligible.sort_values(column).iloc[start:start+n].index
  require(set(selected)==set(meta['changed_row_ids']),'row_independent_mechanism')
  verify_metrics(meta,z,None,list(bank.index),['row'])

# Recompute provenance-priority capacity without treating binary flags as confidence scores.
priority=O/'hard_priority_budget_results.csv'
if priority.exists():
 df=pd.read_csv(priority)
 for sid,group in df.groupby('scenario',sort=False):
  meta=json.loads((O/'scenarios'/(sid+'.json')).read_text());pop=json.loads((O/(meta['dataset']+'_population.json')).read_text());ids=pop['parts']['evaluation'];cols=pop['evaluated_targets'];z=np.load(O/'predictions'/(sid+'.npz'));hard=order(z['A'],ids,cols);stat=order(z['B']&~z['A'],ids,cols);t=set(map(tuple,np.argwhere(z['truth'])));cache={}
  for row in group.to_dict('records'):
   method=row['method'];k=int(np.ceil(len(ids)*row['budget_per_1000']/1000));d=cache.setdefault(method,order(z[method]&~z['A'],ids,cols));seq=hard+stat+d if row['policy']=='control_first' else hard+[x for pair in itertools.zip_longest(stat,d) for x in pair if x is not None];selected=set(list(dict.fromkeys(seq))[:k]);base=set((hard+stat)[:k])
   require(row['hits']==len(selected&t) and row['net_hits']==len(selected&t)-len(base&t),'provenance_priority_budget_recount')
   require(len(selected)<=k and (len(hard)>k or set(hard)<=selected),'hard_control_priority_preserved')

# Real CLI executions, not merely existence of code.
for folder in ['service_demo','service_native_demo']:
 meta=json.loads((O/folder/'report.json').read_text());require(meta['counts']['basic_controls']==2,'service_known_operational_mutations');require(meta['recommendation']=='INSUFFICIENT_EVIDENCE','service_does_not_adopt_from_unlabelled_alerts')
fixture=json.loads((O/'engineering_fixture.json').read_text());require(len(fixture['scenarios'])==8 and not fixture['untouched_findings'],'engineering_fixture_cases_and_untouched')
require(all(p['exit_code']==0 for p in fixture['cli_executions']),'registered_source_cli_executed')
registered=json.loads((O/'service_registered_intervention.json').read_text());registered_dir=R/'data/registered_service_intervention'
registry=json.loads((R/'data/service_registry/synthetic_finance_demo.json').read_text());source=Path(registry['source'])
require(hashlib.sha256(source.read_bytes()).hexdigest()==registered['source_sha256']==registry['source_sha256'] and registered['original_source_unchanged'],'registered_intervention_source_preserved')
logs=json.loads((registered_dir/'injection_values.json').read_text());dirty=pd.read_csv(registered_dir/'dirty_copy.csv',dtype=str,keep_default_na=False).set_index('source_row_id');original=pd.read_csv(source,dtype=str,keep_default_na=False);original.index=[f'synthetic_finance_demo:{i}' for i in range(len(original))]
require(int((dirty!=original[dirty.columns]).to_numpy().sum())==len(logs)==registered['intended_changes']==registered['realized_changes']==9,'registered_intervention_exact_copy_changes')
for entry in logs:
 require(original.at[entry['row_id'],entry['column']]==entry['original'] and dirty.at[entry['row_id'],entry['column']]==entry['new']=='INVALID_NUMERIC','registered_intervention_logged_type_failure')
verify_metrics(registered,np.load(registered_dir/'predictions.npz'),None,list(dirty.index),registry['contract']['targets'])
model=json.loads((O/'local_llm/result.json').read_text());require(model['exit_code']==0 and model['source_context'].startswith('public schema only'),'local_llm_actual_execution_without_test_labels')
require(all(x['state'].startswith('REJECTED') or 'DUPLICATE_BASELINE' in x['state'] or 'SCHEMA_CANDIDATE_NOT_EVALUATED' in x['state'] for x in model['candidates']) and all(x['incremental_detection_claim']=='NONE' for x in model['candidates']),'llm_candidates_no_unverified_incremental_claim')
for item in model['candidates']:
 rule=item['candidate'];state=item['state']
 if state.startswith('VALID'):
  require(rule['values'] in [None,[]] if rule['operator'] in ['integer','numeric_nonnegative'] else rule['column']=='contact' and set(rule['values'])=={'cellular','telephone'},'llm_valid_parameters_against_public_contract')
  require(rule['column'] in (['campaign','previous'] if rule['operator']=='integer' else ['age','campaign','previous','duration'] if rule['operator']=='numeric_nonnegative' else ['contact']),'llm_valid_columns_against_public_contract')
  if 'DUPLICATE_BASELINE' in state:
   contract=json.loads((O/'bank_contracts.json').read_text())['contract'][rule['column']]
   require(rule['operator']=='numeric_nonnegative' and contract['bounds'][0]==0,'llm_duplicate_check_exists_in_executed_contract')
out={'status':'PASSED','checks':dict(checks),'total_assertions':sum(checks.values()),'scope':'Independent raw-reference, cached-prediction, policy, row-mechanism and transformation arithmetic; no independent human semantic adjudication.'}
(R/'evidence/thesis_pilot/supplement_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
