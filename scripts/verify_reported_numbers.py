"""Check rendered tables and headline counts independently against saved machine outputs."""
import gzip,hashlib,json,re
from pathlib import Path
import pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'results/thesis_pilot';P=R/'reports/thesis_pilot';checks=[]
def check(name,ok):
 checks.append({'check':name,'status':'PASSED' if ok else 'FAILED'})
 if not ok:raise AssertionError(name)
manifest=json.loads((O/'analysis_manifest.json').read_text());raw=gzip.decompress((O/'all_metrics.csv.gz').read_bytes());df=pd.read_csv(O/'all_metrics.csv.gz')
check('metric_csv_hash_and_count',hashlib.sha256(raw).hexdigest()==manifest['metrics_sha256'] and len(df)==manifest['metric_rows']==52740)
check('unique_final_scenarios',df.scenario.nunique()==630)
text=(P/'experimental_results.md').read_text()
for row in pd.read_csv(O/'primary_alteration_reference_table.csv').to_dict('records'):
 expected='| '+' | '.join([row['dataset'],row['family'],row['method'],f"{row['mean_extra_hits']:.3f}",f"{row['mean_extra_alerts']:.3f}",f"{row['mean_incremental_recall']:.3f}"])+' |'
 check('report_increment:'+row['dataset']+':'+row['family']+':'+row['method'],expected in text)
for row in pd.read_csv(O/'primary_budget_table.csv').to_dict('records'):
 expected='| '+' | '.join([row['dataset'],row['family'],row['method'],f"{row['mean_net_hits']:.3f}",f"{row['mean_lost_hits']:.3f}"])+' |'
 check('report_budget:'+row['dataset']+':'+row['family']+':'+row['method'],expected in text)
for name in ['executive_summary.md','research_design.md','dataset_qualification.md','rule_baselines.md','injection_validation.md','detector_reproduction.md','experimental_results.md','external_validation.md','incremental_value_analysis.md','domain_issues_and_repairs.md','literature_and_novelty.md','engineering_artifact.md','final_recommendation.md','independent_audit.md']:
 check('required_report:'+name,(P/name).stat().st_size>200)
accept=json.loads((O/'acceptance.json').read_text());check('acceptance_matches_outputs',accept['primary_cell_scenarios']==630 and accept['bank_row_scenarios']==len(json.loads((O/'bank_crossfield_rows/results.json').read_text()))==45)
llm=json.loads((O/'local_llm/result.json').read_text());check('llm_prompt_response_provenance',hashlib.sha256((O/'local_llm/prompt.txt').read_bytes()).hexdigest()==llm['prompt_sha256'] and hashlib.sha256((O/'local_llm/response.txt').read_bytes()).hexdigest()==llm['response_sha256'])
check('no_semantic_adoption_claim',accept['research_feasibility']=='CONDITIONAL_GO' and accept['novelty'].startswith('NOT_ESTABLISHED'))
test_count=int(re.findall(r'(\d+) passed',(R/'evidence/thesis_pilot/all_tests.log').read_text())[-1]);check('test_count_matches_executed_log',accept['tests'].startswith(f'{test_count} PASSED') and f'{test_count} tests passed' in (P/'executive_summary.md').read_text())
rules=json.loads((R/'manifests/thesis_pilot/rule_provenance.json').read_text())['controls'];categories={'DOCUMENTED_SOURCE_CONTRACT','EXPLICIT_STIPULATED_CONTRACT','TRAINING_ONLY_STATISTICAL_CONTROL','EXPERIMENTAL_HEURISTIC'}
check('every_applied_control_has_separate_provenance',all(r['provenance'] in categories and r['evidence'] and r['parameters'] for r in rules))
check('requiredness_is_explicitly_stipulated',sum(r['control']=='requiredness' for r in rules)==12 and all(r['provenance']=='EXPLICIT_STIPULATED_CONTRACT' for r in rules if r['control']=='requiredness'))
code=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((R/'src/thesis_pilot').glob('*.py')))+(R/'scripts/native_detector_worker.py').read_bytes()).hexdigest();protocol=hashlib.sha256((R/'configs/thesis_pilot/protocol_v1.json').read_bytes()).hexdigest()
check('all_final_cases_match_current_frozen_code_and_protocol',all(d['code_sha256']==code and d['protocol_sha256']==protocol for d in (json.loads(p.read_text()) for p in (O/'scenarios').glob('*.json'))))
result={'status':'PASSED','checks':len(checks),'details':checks};(R/'evidence/thesis_pilot/report_verification.json').write_text(json.dumps(result,indent=2));print('PASSED',len(checks),'report/output consistency checks')
