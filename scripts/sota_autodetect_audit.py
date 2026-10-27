"""Released candidate annotations only; no method execution or population recall."""
import collections,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];base=R/'data/sources/Auto-Detect';seen=collections.defaultdict(set);rows=[]
for path in sorted((base/'labeled_output').glob('*.tsv')):
 counts=collections.Counter();issues=collections.Counter()
 for line in path.read_bytes().decode('latin-1').split('\n'):
    if not line:continue
    line=line.rstrip('\r')
    values=line.split('\t')
    if len(values)!=9:issues['invalid_fields']+=1;continue
    try:label=int(values[-1])
    except ValueError:issues['invalid_label']+=1;continue
    if label not in [0,1,2]:issues['invalid_label']+=1;continue
    counts[label]+=1;seen[tuple(values[:7])].add(label)
 n=counts[0]+counts[2];rows.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sampled_candidates':sum(counts.values()),'compatible':counts[0],'ambiguous':counts[1],'incompatible':counts[2],'candidate_precision_excluding_ambiguous':counts[2]/n if n else None,'issues':dict(issues)})
out={'source_revision':'fdb40813eb426b776b4b74ed9335fa513d3d292a','unit':'publisher-labelled incompatible value pair, conditional on released method and sampled rank stratum','rows':rows,'byte_decoding':'Latin-1 lossless byte mapping; some original files contain non-UTF8 bytes; labels are ASCII','duplicate_candidate_label_conflicts':sum(len(v)>1 for v in seen.values()),'definite_compatible_vs_incompatible_conflicts':sum({0,2}<=v for v in seen.values()),'distinct_annotated_candidates':len(seen),'no_exhaustive_recall':'Unlabelled candidates are not negatives; top-ranked sampling not population representative','native_method_execution':'NOT_CLAIMED; released human-labelled output assessment, not re-execution'}
p=R/'results/sota_followup/autodetect_candidates.json';old=json.loads(p.read_text()) if p.exists() else out;assert sorted(old['rows'],key=lambda x:x['file'])==out['rows'];assert old['distinct_annotated_candidates']==out['distinct_annotated_candidates'];assert old['duplicate_candidate_label_conflicts']==out['duplicate_candidate_label_conflicts'];p.write_text(json.dumps(out,indent=2)+'\n');print(len(rows),sum(v['sampled_candidates'] for v in rows),len(seen),out['definite_compatible_vs_incompatible_conflicts'])
