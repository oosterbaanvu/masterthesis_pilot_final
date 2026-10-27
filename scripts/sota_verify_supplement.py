"""Independent raw-source, coordinate and budget recount. No production imports."""
import ast,collections,csv,hashlib,itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'results/sota_followup';checks=collections.Counter()
def ok(value,tag):
    if not value:raise AssertionError(tag)
    checks[tag]+=1
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def coord(a):return set(map(tuple,np.argwhere(a)))
def hashorder(items,key):return sorted(items,key=lambda i:hashlib.sha256(key(i).encode()).digest())
def queue(h,b,d,k,policy):
    seen=set(h);b=[i for i in b if i not in seen];d=[i for i in d if i not in seen];tail=b+d if policy=='control_first' else [i for pair in itertools.zip_longest(b,d) for i in pair if i is not None];result=[]
    for i in list(h)+tail:
        if i not in result:result.append(i)
        if len(result)==k:break
    return set(result)
def same(row,expected,tag):
    for k,v in expected.items():ok(float(row[k])==v,tag+'_'+k)
def check_cells(rows,z,u,ids,columns):
    masks={k:coord(v) for k,v in z.items()};t=masks.pop('truth');orders={k:hashorder(v,lambda ij:f'{ids[ij[0]]}|{columns[ij[1]]}') for k,v in masks.items()};prior={k:coord(v) for k,v in u.items()}
    for m in rows:
        b=masks[m['baseline']];a=masks[m['method']]
        if m['mode']=='budget_union':
            k=int(np.ceil(len(ids)*m['budget']/1000));s=queue(orders['R'],orders[m['baseline']],orders[m['method']],k,m['policy']);bs=set(orders[m['baseline']][:0]) # explicit hard-first baseline below
            bs=queue(orders['R'],orders[m['baseline']],[],k,m['policy']);same(m,{'capacity':k,'reviewed':len(s),'hits':len(s&t),'alerts':len(s),'extra_hits':len((s-bs)&t),'lost_hits':len((bs-s)&t),'net_hits':len(s&t)-len(bs&t)},'cell_budget')
        else:
            s=a if m['mode']=='alone' else a|b;same(m,{'hits':len(s&t),'alerts':len(s),'extra_hits':len((s-b)&t),'extra_alerts':len(s-b),'new_detector_hits':len((a-prior[m['method']])&t),'off_reference_alerts_unknown':len(s-t)},'cell_increment')
def check_values(rows,frame,ids):
    n=len(frame);truth=set(np.flatnonzero(frame.publisher_positive.to_numpy(bool)));amb=set(np.flatnonzero(frame.ambiguous.to_numpy(bool)));allids=set(range(n));methods=[k for k in frame if k not in ['column_position','value_position','publisher_positive','ambiguous','header','column_id'] and not k.endswith('_confidence')];masks={};eligible={}
    for k in methods:
        if frame[k].dtype==object:continue
        eligible[k]=set(np.flatnonzero(frame[k].notna().to_numpy()));masks[k]=set(np.flatnonzero(frame[k].fillna(False).astype(bool).to_numpy()))
    order={k:hashorder(v,lambda i:ids[i]) for k,v in masks.items()}
    for m in rows:
        method=m['method'];e=eligible[method];a=masks[method];target=(truth-amb)&e;h=masks['R']&e;b=masks['R' if m['baseline']=='R' else 'RS']&e
        if m['baseline']=='RS_pretrained_pattern_native':b|=masks['AutoTest_pattern_native']&e
        same(m,{'eligible_values':len(e),'reference_positives':len(target)},'value_universe')
        if m['mode']=='budget_union':
            ho=hashorder(h,lambda i:ids[i]);bo=hashorder(b,lambda i:ids[i]);do=order[method]
            if m['policy']=='native_ranked_equal_share':do=sorted(a,key=lambda i:(-float(frame.iloc[i][method+'_confidence']),hashlib.sha256(ids[i].encode()).digest()))
            s=queue(ho,bo,do,int(m['capacity']),m['policy']);bs=queue(ho,bo,[],int(m['capacity']),m['policy']);same(m,{'reviewed':len(s),'hits':len(s&target),'alerts':len(s),'ambiguous_alerts':len(s&amb),'extra_hits':len((s-bs)&target),'lost_hits':len((bs-s)&target),'net_hits':len(s&target)-len(bs&target)},'value_budget')
        else:
            s=a if m['mode']=='alone' else a|b;same(m,{'hits':len(s&target),'alerts':len(s),'ambiguous_alerts':len(s&amb),'reference_nonpositive_alerts':len((s& (e-amb))-target),'extra_hits':len((s-b)&target),'extra_alerts':len(s-b)},'value_increment')
def publisher():
    metrics=pd.read_csv(O/'published_value_metrics.csv')
    for name in ['rt','st']:
        frame=pd.read_csv(O/f'values/{name}_coordinate_outputs.csv.gz');positions={pair:i for i,pair in enumerate(zip(frame.column_position,frame.value_position))};seen=set();count=0;positive=0;ambiguous=0
        with (R/f'data/raw/qixuchen__AutoTest/benchmarks/{name}_bench.csv').open(encoding='utf-8-sig',newline='') as stream:
            for p,row in enumerate(csv.DictReader(stream)):
                if all(v=='' for v in row.values()):continue
                rid=row['index'];duplicate=rid in seen;seen.add(rid)
                try:v,t,a=[ast.literal_eval(row[k]) for k in ['dist_val','ground_truth','ground_truth_debatable']]
                except (SyntaxError,ValueError):continue
                if duplicate or not all(isinstance(q,list) and all(isinstance(x,str) for x in q) for q in [v,t,a]) or len(v)!=len(set(v)) or len(v)!=int(row['dist_val_count']) or not set(t+a)<=set(v) or set(t)&set(a):continue
                count+=1;positive+=len(t);ambiguous+=len(a)
                for j,x in enumerate(v):
                    z=frame.iloc[positions[(p,j)]];ok(bool(z.publisher_positive)==(x in t) and bool(z.ambiguous)==(x in a),'publisher_raw_label_mapping')
        ok((count,positive,ambiguous)==((1194,41,35) if name=='rt' else (1193,45,77)),'publisher_qualification_counts')
        ok(len(frame)==(90934 if name=='rt' else 71719),'publisher_value_count');ids=[f'{name}:{c}:{v}' for c,v in zip(frame.column_position,frame.value_position)];check_values(metrics[metrics.benchmark==name].to_dict('records'),frame,ids)
def patterns():
    inventories=json.loads((R/'manifests/sota_followup/pattern_sources.json').read_text());sources={}
    for d in inventories:
        p=R/f"data/sources/RIOLU/test_data_profiling/homo/{d['dataset']}.json";ok(sha(p)==d['source_file_sha256'],'pattern_source_hash');raw=json.loads(p.read_text())['Data'];positions=sorted(range(len(raw)),key=lambda i:hashlib.sha256(f"{d['dataset']}:{i}".encode()).hexdigest())[:800];ok(positions==d['source_positions'],'pattern_source_selection');sources[d['dataset']]=([str(raw[i]) for i in positions],[f"{d['dataset']}:{i}" for i in positions],positions)
    count=0
    for p in sorted((O/'pattern_ingest').glob('*.json')):
        d=json.loads(p.read_text());values,ids,sourcepos=sources[d['dataset']];z=dict(np.load(p.with_suffix('.npz')));u=dict(np.load(O/f"pattern_ingest/{d['dataset']}_untouched.npz"));logs=json.loads((R/d['local_log']).read_text());ok(sha(R/d['local_log'])==d['log_sha256'] and sha(p.with_suffix('.npz'))==d['prediction_sha256'],'pattern_output_identity');expected=set()
        for entry in logs:
            i=ids.index(entry['row_id']);v=values[i];ok(entry['original']==v and entry['new']!=v,'pattern_noop_and_source');j=next((j for j,c in enumerate(v) if c in '/-.'),None)
            if d['dataset']=='codes':j=next((j for j,c in enumerate(v) if c.isdigit()),j)
            new=v[:j]+('O' if d['dataset']=='codes' else '_')+v[j+1:] if j is not None else v+'@';ok(entry['new']==new,'pattern_independent_replacement');expected.add(i)
        n=int(800*d['rate']);rng=np.random.default_rng(d['seed'])
        if d['mechanism']=='ECAR':chosen=set(rng.choice(ids,n,replace=False));chosen={ids.index(i) for i in chosen}
        else:
            v=sourcepos if d['mechanism']=='EAR' else values;start=int(rng.integers(0,800-n));chosen=set(pd.Series(v).sort_values().index[start:start+n])
        ok(expected==set(np.flatnonzero(z['truth']))==chosen and len(expected)==n,'pattern_independent_placement');frame=pd.DataFrame({k:v for k,v in z.items() if k!='truth'});frame['publisher_positive']=z['truth'];frame['ambiguous']=False;check_values(d['metrics'],frame,ids)
        for m in d['metrics']:
            t=z['truth'];method=m['method'];ok(m['newly_triggered_reference_hits']==int((t&~u[method].astype(bool)&z[method].astype(bool)).sum()),'pattern_counterpart_new_triggers')
        count+=1
    ok(count==135,'pattern_case_count')
def categorical():
    metrics=pd.read_csv(O/'categorical_baseline/metrics.csv.gz');count=0
    for sid,group in metrics.groupby('scenario',sort=False):
        d=json.loads((O/'ingest'/(sid+'.json')).read_text());pop=json.loads((O/f"ingest/{d['dataset']}_{d['view']}_population.json").read_text());base=dict(np.load(O/'ingest'/(sid+'.npz')));u0=dict(np.load(O/f"ingest/{d['dataset']}_{d['view']}_untouched.npz"));extra=dict(np.load(O/'categorical_baseline'/(sid+'.npz')));u=dict(np.load(O/f"categorical_baseline/{d['dataset']}_{d['view']}_untouched.npz"));ok(np.all(~base['RSM']|extra['RSM_LR995']) and np.all(~extra['RSM_LR995']|extra['RSM_LR95']),'categorical_baseline_nesting')
        for label,g in group.groupby('baseline'):
            z={**base,'RSM_Ridge':base['RSM'],label:extra[label]};prior={**u0,'RSM_Ridge':u0['RSM'],label:u[label]};check_cells(g.to_dict('records'),z,prior,pop['parts']['evaluation'],pop['targets'])
        count+=1
    ok(count==720,'categorical_case_count')
def boundary():
    result=json.loads((O/'cdc_boundary/results.json').read_text())
    for d in result:
        z=dict(np.load(O/f"cdc_boundary/{d['dataset']}_{d['mode']}.npz"));ok(np.all(~z['inclusive']|z['released']),'inclusive_interval_subset');ok(int(z['released'].sum())==d['released_total'] and int(z['inclusive'].sum())==d['inclusive_total'],'cdc_diagnostic_totals')
        if d['mode']=='native_types':ok(d['native_untouched_equals_primary'] and np.array_equal(z['released'],np.load(O/f"ingest/{d['dataset']}_full_untouched.npz")['cdc_original']),'canonical_native_CDC_parity')
    paths=list((O/'cdc_boundary/selected_cases').glob('*.json'));ok(len(paths)==16,'cdc_all_eight_cases_two_modes')
    for p in paths:
        d=json.loads(p.read_text());z=dict(np.load(p.with_suffix('.npz')));u=dict(np.load(O/f"ingest/{d['dataset']}_full_untouched.npz"));diag=np.load(O/f"cdc_boundary/{d['dataset']}_{d['mode']}.npz");u.update(cdc_released_diagnostic=diag['released'],cdc_inclusive_endpoints=diag['inclusive']);pop=json.loads((O/f"ingest/{d['dataset']}_full_population.json").read_text());ok(np.all(~z['cdc_inclusive_endpoints']|z['cdc_released_diagnostic']),'changed_inclusive_subset');check_cells(d['metrics'],z,u,pop['parts']['evaluation'],pop['targets'])
def local():
    d=json.loads((O/'zeroed_local_v2/result.json').read_text());z=np.load(O/'zeroed_local_v2/predictions.npz');t=z['truth'];h=z['hard'];a=z['prediction'].astype(bool);e=z['eligible'];same(d,{'synthetic_contract_errors':int(t.sum()),'R_hits':int((h&t&e).sum()),'model_hits':int((a&t&e).sum()),'additional_hits_beyond_R':int((a&~h&t&e).sum()),'model_alerts':int((a&e).sum()),'representative_queries':int((~e).sum())},'local_MLP_raw_recount')
    d=json.loads((R/'evidence/sota_followup/riolu_authors_parity.json').read_text());ok(d['status']=='PASSED','RIOLU_author_parity_evidence')
def extra_sensitivities():
    table=pd.read_csv(O/'published_pattern_priority_sensitivity.csv')
    for name,group in table.groupby('benchmark'):
        f=pd.read_csv(O/f'values/{name}_coordinate_outputs.csv.gz');t=set(np.flatnonzero(f.publisher_positive&~f.ambiguous));amb=set(np.flatnonzero(f.ambiguous));p=set(np.flatnonzero(f.AutoTest_pattern_native));b=set(np.flatnonzero(f.RS));d=set(np.flatnonzero(f.AutoTest_full));ids=[f'{name}:{c}:{v}' for c,v in zip(f.column_position,f.value_position)];order=lambda x:hashorder(x,lambda i:ids[i])
        for row in group.to_dict('records'):
            k=int(row['capacity']);base=set((order(p)+order(b-p))[:k]);selected=queue(order(p),order(b),order(d),k,'equal_share');same(row,{'baseline_hits':len(base&t),'union_hits':len(selected&t),'net_hits':len(selected&t)-len(base&t),'extra_hits':len((selected-base)&t),'lost_hits':len((base-selected)&t),'reviewed':len(selected),'ambiguous_reviews':len(selected&amb)},'pretrained_pattern_priority')
    for sid,g in pd.read_csv(O/'counterpart_increment.csv.gz').groupby('scenario',sort=False):
        z=np.load(O/'ingest'/(sid+'.npz'));first=g.iloc[0];u=np.load(O/f"ingest/{first['dataset']}_{first['view']}_untouched.npz")
        for row in g.to_dict('records'):
            t=z['truth'];a=z[row['method']];prior=u[row['method']];b=z[row['baseline']];same(row,{'extra_hits':int((a&~b&t).sum()),'newly_triggered_extra_hits':int((a&~prior&~b&t).sum()),'already_alerted_extra_hits':int((a&prior&~b&t).sum()),'newly_triggered_extra_alerts':int((a&~prior&~b).sum()),'untouched_detector_alerts':int(prior.sum())},'extra_counterfactual')
    # Recount the human-labelled release using raw newline bytes, excluding no unreviewed candidates.
    d=json.loads((O/'autodetect_candidates.json').read_text());known=collections.defaultdict(set);total=0
    for row in d['rows']:
        path=R/'data/sources/Auto-Detect/labeled_output'/row['file'];ok(sha(path)==row['sha256'],'human_release_hash');c=collections.Counter()
        for line in path.read_bytes().split(b'\n'):
            v=line.rstrip(b'\r').split(b'\t')
            if len(v)!=9 or v[-1] not in [b'0',b'1',b'2']:continue
            c[int(v[-1])]+=1;known[tuple(v[:7])].add(int(v[-1]))
        same(row,{'compatible':c[0],'ambiguous':c[1],'incompatible':c[2],'sampled_candidates':sum(c.values())},'human_release_recount');total+=sum(c.values())
    ok(total==4339 and len(known)==4006 and sum({0,2}<=v for v in known.values())==19,'human_annotation_population')

if __name__=='__main__':
    for fn in [publisher,patterns,categorical,boundary,local,extra_sensitivities]:fn();print(fn.__name__,'passed',flush=True)
    d={'status':'PASSED','checks':dict(checks),'assertions':sum(checks.values()),'scope':'Pinned publisher input labels; value and P5 predictions and budgets; categorical baseline counters and masks; canonical CDC diagnostic masks; local MLP raw counts. No independent semantic annotation or reimplementation of neural inference.'};(R/'evidence/sota_followup/supplementary_verification.json').write_text(json.dumps(d,indent=2)+'\n');print(d['assertions'])
