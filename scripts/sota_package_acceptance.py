"""Delivery integrity: outputs, immutable prior experiment trees and report links."""
import hashlib,json,re,subprocess
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'results/sota_followup';checks=0
def require(value):
 global checks
 assert value;checks+=1
require(json.loads((R/'evidence/sota_followup/ingest_verification.json').read_text())['status']=='PASSED');require(json.loads((R/'evidence/sota_followup/supplementary_verification.json').read_text())['status']=='PASSED')
cases=[json.loads(p.read_text()) for p in (O/'ingest').glob('*.json') if 'scenario' in json.loads(p.read_text())];require(len(cases)==720);require(len({tuple(d[k] for k in ['dataset','family','mechanism','rate','seed']) for d in cases})==360);require(all(not d['failures'] for d in cases));require(len(pd.read_csv(O/'ingest_metrics.csv.gz'))==120960);require(len(list((O/'pattern_ingest').glob('*.json')))==135)
reports=sorted((R/'reports/sota_followup').glob('*.md'));require(len(reports)==12)
for p in reports:
 for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  if not target.startswith(('http:','https:','#')):require((p.parent/target).exists())
for root in ['reports/thesis_pilot','results/thesis_pilot','manifests/thesis_pilot','src/thesis_pilot']:
 require(not subprocess.check_output(['git','diff','46b9f3171aa9200b5b1cc97bb97ed70b2b38082b','--',root],cwd=R))
npz=0
for p in O.rglob('*.npz'):
 z=np.load(p,allow_pickle=False)
 for k in z.files:require(z[k].dtype.kind in 'bifu')
 npz+=1
require(json.loads((R/'evidence/sota_followup/log_restoration_test.json').read_text())['all_byte_identical'])
for method in ['riolu_original','riolu_small_sample','lucario_transductive','autotest_pattern_only']:
 d=json.loads((O/'service_demo'/method/'report.json').read_text());require(d['source_unchanged'] and d['eligible_columns']==1 and d['alerts']==10)
# Store a SHA inventory after all summaries/reports are final. The inventory does not hash itself.
files=[]
for directory in ['results/sota_followup','reports/sota_followup','configs/sota_followup','envs/sota_followup']:
 for p in sorted((R/directory).rglob('*')):
  if p.is_file():files.append({'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(R/'manifests/sota_followup/artifact_hashes.json').write_text(json.dumps(files,indent=2)+'\n');d={'status':'PASSED','checks':checks,'numeric_mask_archives':npz,'hashed_artifacts':len(files),'old_four_trees_unchanged':True,'new_full_tables':0,'new_logical_source_alteration_cases':495,'new_scored_context_or_occurrence_cases':855,'reports':12,'science':'Exploratory only, no natural semantic gold or confirmed novelty'};(R/'evidence/sota_followup/package_acceptance.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
