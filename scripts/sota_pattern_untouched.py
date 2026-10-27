"""Persist unchanged P5 predictions; same frozen inputs/settings, no error labels."""
import hashlib,json
from pathlib import Path
import numpy as np
from sota_followup.pattern_adapter import BoundedPatternWorker
from sota_followup.benchmarks import AutoTestPattern,statistical_flags
R=Path(__file__).resolve().parents[1];O=R/'results/sota_followup/pattern_ingest';auto=AutoTestPattern()
workers={m:BoundedPatternWorker(m) for m in ['riolu_original','lucario_transductive']}
try:
 for s in json.loads((R/'manifests/sota_followup/pattern_sources.json').read_text()):
    p=R/f"data/sources/RIOLU/test_data_profiling/homo/{s['dataset']}.json";assert hashlib.sha256(p.read_bytes()).hexdigest()==s['source_file_sha256'];raw=json.loads(p.read_text())['Data'];values=[str(raw[i]) for i in s['source_positions']]
    flags={'R':np.zeros(800,bool),'RS':statistical_flags(values),'AutoTest_pattern_only':auto.score_columns([{'position':0,'header':s['dataset'],'values':values}])[0][0]}
    for m,w in workers.items():flags[m]=w.score(values)['flags']
    np.savez_compressed(O/(s['dataset']+'_untouched.npz'),**flags)
finally:
 for w in workers.values():w.close()
