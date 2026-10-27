"""Bounded native-crash diagnosis, and a separately named compatibility repair."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'));sys.path.insert(0,str(R/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO'))
from native_detector_worker import lucario_fit,lucario_score
from detectors.pattern import PatternDetector
from detectors.utils import Utils
original=PatternDetector.detect_templates
def aligned(self):
    original(self)
    if len(self.delimiter_bags)!=len(self.accepted_templates):
        bags={}
        for value in self.data:
            template,_,bag=Utils.record_info(self.special_char,str(value))
            if template not in bags:bags[template]=bag
        self.delimiter_bags=[bags[t] for t in self.accepted_templates]
def predict(values,fix):
    PatternDetector.detect_templates=aligned if fix else original;np.random.seed(42);df=pd.DataFrame({'value':values});return lucario_score(df,lucario_fit(df))[:,0]
rows=json.loads((R/'data/sota_followup/autotest_input_rt.json').read_text());selected=rows[:20];lookup={r['position']:r for r in rows};failures=[]
for p in sorted((R/'data/sota_followup/value_checkpoint_v3/rt').glob('*.json'),key=lambda p:int(p.stem)):
    d=json.loads(p.read_text())
    if d['results']['lucario_transductive']['status']=='BLOCKED_SOFTWARE':failures.append(int(p.stem))
selected+= [lookup[i] for i in failures[:5] if i not in {r['position'] for r in selected}];result=[];arrays={}
for row in selected:
    item={'column_position':row['position'],'values':len(row['values'])}
    try:before=predict(row['values'],False);item['native']='EXECUTED'
    except Exception as e:before=None;item.update({'native':'BLOCKED_SOFTWARE','error':repr(e)})
    try:
        after=predict(row['values'],True);item['compatibility']='EXECUTED';item['compatibility_alerts']=int(after.sum());arrays[str(row['position'])+'_fixed']=after
        if before is not None:item['unchanged_existing_flags']=bool(np.array_equal(before,after));arrays[str(row['position'])+'_original']=before
    except Exception as e:item.update({'compatibility':'BLOCKED','repair_error':repr(e)})
    result.append(item)
PatternDetector.detect_templates=original
O=R/'results/sota_followup/lucario_alignment';O.mkdir(exist_ok=True);np.savez_compressed(O/'probe_flags.npz',**arrays)
meta={'status':'EXPLICIT_COMPATIBILITY_ADAPTATION','cause':'Multiple equally frequent raw templates leave cut=-1. Released detect_templates retains accepted_templates but never fills delimiter_bags; match_into_templates then indexes an empty list.','repair':'After original selection, reconstruct each retained template\'s first observed delimiter bag using original Utils.record_info; do not remove records/templates or alter coverage parameters.','selection':'First20 RT columns and first5 software failures, selected without reference labels','cases':result,'scope':'Limited diagnosis and compatibility probe, not replacement of primary native LUCARIO or full repaired benchmark execution','semantic_correctness':'NOT_ESTABLISHED','method_family':'same LUCARIO family, not a new detector'};(O/'result.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
