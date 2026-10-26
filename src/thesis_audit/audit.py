"""Deterministic audit, conservative semantic statuses, no source mutations."""
import ast
import collections
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
from .acquire import digest

STATUSES=['VERIFIED_REFERENCE_ERROR','CONTROLLED_INJECTION_ERROR','REPRESENTATION_ONLY','DEBATABLE_OR_UNCERTAIN','UNVERIFIED_REPAIR','NOT_AN_ERROR','UNKNOWN']
NUMERIC={
 'raha_tax':{'salary','rate','single_exemp','married_exemp','child_exemp'},
 'cars':{'MPG','Cylinders','Displacement','Horsepower','Weight','Acceleration','Model'},
 'raha_movies_1':{'year','rating_value','rating_count','review_count'},
 'raha_beers':{'ounces','abv','ibu'},
}

def read_table(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:
        r=csv.reader(f);header=next(r);rows=list(r)
    if len(set(header))!=len(header): raise ValueError('Duplicate headers')
    if any(len(row)!=len(header) for row in rows): raise ValueError('Ragged rows')
    return header,rows

def equivalent_number(x,y):
    try:
        a,b=Decimal(x),Decimal(y)
        return a.is_finite() and b.is_finite() and a==b
    except InvalidOperation:return False

def classify(name,col,x,y):
    if x==y:return 'NOT_AN_ERROR','literal reference agreement; not a semantic correctness certificate'
    if col in NUMERIC.get(name,set()) and equivalent_number(x,y):
        return 'REPRESENTATION_ONLY','finite Decimal equivalence on explicitly numerical field'
    if name in {'cars','restaurant'} and x=='?' and y not in {'','?'}:
        return 'DEBATABLE_OR_UNCERTAIN','published generated missingness alteration; requiredness contract not established, so not a verified DQ violation'
    if name=='raha_beers' and col=='ounces':
        m=re.fullmatch(r'([0-9.]+)\s*(?:oz\.?|ounce[s]?)',x)
        if m and equivalent_number(m[1],y):
            return 'DEBATABLE_OR_UNCERTAIN','unit-bearing equal magnitude; representation candidate conditional on source unit contract'
    if name=='raha_tax' and col=='zip' and x.lstrip('0')==y.lstrip('0'):
        return 'DEBATABLE_OR_UNCERTAIN','reference removes postal leading zeros; identifier must not be numerically normalized'
    if name=='raha_beers' and col=='abv' and '%' in x:
        return 'DEBATABLE_OR_UNCERTAIN','percent suffix and fraction convention require authoritative scale interpretation'
    return 'DEBATABLE_OR_UNCERTAIN','published disagreement; semantic correction and provenance of this cell not independently verified'

def profile(p):
    h,r=read_table(p);out={'rows':len(r),'columns':len(h),'schema':h,'duplicate_rows':len(r)-len(set(map(tuple,r))),'fields':{}}
    for j,k in enumerate(h):
        vals=[x[j] for x in r];c=collections.Counter(vals)
        out['fields'][k]={'storage_type':'string','empty':c[''],'literal_tokens':{t:c[t] for t in ['N/A','NA','NULL','null','?','-1','unknown'] if c[t]},'distinct':len(c),'unique':len(c)==len(r),'leading_zero_count':sum(bool(re.match(r'^0\d',v)) for v in vals)}
    return out

def audit_pair(name,dirty,clean,out):
    h,d=read_table(dirty);hc,c=read_table(clean)
    if len(d)!=len(c):raise ValueError('Row-count mismatch '+name)
    schema_maps=json.loads(Path('configs/schema_maps.json').read_text())
    if h!=hc and schema_maps.get(name,{}).get('dirty')!=h:raise ValueError('Unregistered dirty schema '+name)
    if h!=hc and schema_maps[name]['reference']!=hc:raise ValueError('Unregistered reference schema '+name)
    ids=[k for k in ['index','tuple_id','id','name','Car'] if k in h]
    identity={}
    for k in ids:
        j=h.index(k);identity[k]={'dirty_unique':len({x[j] for x in d})==len(d),'reference_unique':len({x[j] for x in c})==len(c),'positional_equal':all(x[j]==y[j] for x,y in zip(d,c)),'changed':sum(x[j]!=y[j] for x,y in zip(d,c))}
    counts=collections.Counter();bycol={};samples=[];seen=collections.Counter();x_sub=0;changed=0
    path=out/(name+'_labels.csv');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['row_position_zero_based','column','original','reference','status','reason'])
        for i,(a,b) in enumerate(zip(d,c)):
            for j,col in enumerate(h):
                x,y=a[j],b[j];status,reason=classify(name,col,x,y);counts[status]+=1
                if x==y:continue
                changed+=1;bycol.setdefault(col,collections.Counter())[status]+=1
                w.writerow([i,col,x,y,status,reason])
                if len(x)==len(y) and all(u==v or u=='x' for u,v in zip(x,y)):x_sub+=1
                key=(col,status)
                if seen[key]<3:samples.append({'dataset':name,'row':i,'column':col,'original':x,'reference':y,'status':status,'reason':reason})
                seen[key]+=1
    (out/(name+'_sample.json')).write_text(json.dumps(samples,indent=2,ensure_ascii=False)+'\n')
    blind=[{k:v for k,v in x.items() if k not in {'status','reason'}}|{'review_decision':None,'evidence':None} for x in samples]
    (out/(name+'_blind_review.json')).write_text(json.dumps(blind,indent=2,ensure_ascii=False)+'\n')
    return {'name':name,'shape':[len(d),len(h)],'raw_differences':changed,'counts':dict(counts),'differences_by_column':bycol,'identity':identity,'x_substitution_candidates':x_sub,'generated_missingness_candidates':sum(a[j]=='?' and b[j] not in {'','?'} for a,b in zip(d,c) for j in range(len(h))) if name in {'cars','restaurant'} else 0,'alignment_status':'POSITIONAL_WITH_ANCHORS' if any(v['positional_equal'] and v['dirty_unique'] for v in identity.values()) else 'POSITIONAL_ONLY_NOT_PROVEN','sample_count':len(samples),'labels_sha256':digest(path)}

def parse_list(s):
    if s=='':raise ValueError('Missing list is unknown, not []')
    try:v=ast.literal_eval(s)
    except (ValueError,SyntaxError) as e:raise ValueError('Invalid list literal') from e
    if not isinstance(v,list) or not all(isinstance(x,str) for x in v):raise ValueError('Expected list of strings')
    return v

def audit_column_bench(p,out):
    counts=collections.Counter();issues=[];eligible=[];identifiers=set();canonical=[];samples=[]
    with Path(p).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        for pos,row in enumerate(reader):
            counts['physical_records']+=1
            if all(v=='' for v in row.values()):counts['fully_empty_records']+=1;continue
            counts['nonempty_columns']+=1
            rid=row['index'];problems=[]
            if rid in identifiers:problems.append('DUPLICATE_INDEX')
            identifiers.add(rid)
            vals={}
            for field in ['dist_val','ground_truth','ground_truth_debatable']:
                try:vals[field]=parse_list(row[field])
                except ValueError as e:problems.append(field+': '+str(e))
            if len(vals)==3:
                v,g,b=map(lambda k:vals[k],['dist_val','ground_truth','ground_truth_debatable'])
                if len(set(v))!=len(v):problems.append('DISTINCT_VALUE_LIST_HAS_DUPLICATES')
                if int(row['dist_val_count'])!=len(v):problems.append('DISTINCT_COUNT_MISMATCH')
                if not set(g+b)<=set(v):problems.append('ANNOTATION_OUTSIDE_UNIVERSE')
                if set(g)&set(b):problems.append('CONTRADICTORY_LABEL')
                counts['parsed_values_all_columns']+=len(v);counts['published_positive_all_parsed']+=len(g);counts['debatable_all_parsed']+=len(b)
            if problems:
                issues.append({'record_position':pos,'index':rid,'problems':problems});counts['excluded_columns']+=1;continue
            counts['eligible_columns']+=1;counts['eligible_values']+=len(v);counts['published_positive']+=len(g);counts['published_debatable']+=len(b)
            eligible.append(rid)
            canonical.append(hashlib.sha256(json.dumps([row['header'],sorted(v)],ensure_ascii=False).encode()).hexdigest())
            if g or b:samples.append({'index':rid,'header':row['header'],'published_unambiguous':g,'published_debatable':b,'independent_review':None})
    name=Path(p).stem
    (out/(name+'_annotation_review.json')).write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n')
    return {'name':name,'counts':dict(counts),'issues':issues,'eligible_ids':eligible,'column_fingerprints':canonical,'duplicate_content_columns':len(canonical)-len(set(canonical)),'source_table_identity':'NOT_PROVIDED','occurrence_frequencies':'NOT_PROVIDED','semantic_verification':'PUBLISHER_ANNOTATION_ONLY'}

def main():
    root=Path('.');out=root/'data/derived';out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((root/'manifests/files.json').read_text());profiles={}
    for x in manifest:
        if digest(root/x['path'])!=x['sha256']:raise ValueError('Integrity failure')
        if x['path'].endswith('.csv') and '/benchmarks/' not in x['path']:profiles[x['path']]=profile(root/x['path'])
    (root/'evidence/file_profiles.json').write_text(json.dumps(profiles,indent=2)+'\n')
    pairs=[]
    for p in sorted((root/'data/raw/BigDaMa__raha/datasets').glob('*/dirty.csv')):
        pairs.append(audit_pair('raha_'+p.parent.name,p,p.with_name('clean.csv'),out))
    for name in ['cars','restaurant']:
        p=root/'data/raw/calgo-lab__error-paper/data'/name
        pairs.append(audit_pair(name,p/(name+'_3_1.csv'),p/'clean.csv',out))
    (root/'evidence/pair_audits.json').write_text(json.dumps(pairs,indent=2)+'\n')
    cols=[audit_column_bench(root/'data/raw/qixuchen__AutoTest/benchmarks'/f,out) for f in ['rt_bench.csv','st_bench.csv']]
    (root/'evidence/column_audits.json').write_text(json.dumps(cols,indent=2)+'\n')
    print(json.dumps({'pairs':[{k:x[k] for k in ['name','shape','raw_differences','alignment_status']} for x in pairs],'columns':[{k:x[k] for k in ['name','counts','issues','duplicate_content_columns']} for x in cols]},indent=2))
if __name__=='__main__':main()
