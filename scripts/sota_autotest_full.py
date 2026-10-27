"""Python3.7 original author online inference using released full SDCs and feature caches.
Only paths and process counts are adapted. Labels never enter the native pipeline.
"""
import argparse,ast,collections,contextlib,hashlib,json,os,resource,sys,time,traceback
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    p=argparse.ArgumentParser();p.add_argument('--benchmark',choices=['rt','st'],required=True);p.add_argument('--corpus',choices=['rt_train','st_train','tablib'],default='rt_train');p.add_argument('--limit',type=int);args=p.parse_args()
    root=Path(__file__).resolve().parents[1];source=root/'data/sota_followup/autotest37_source';local=root/'data/sota_followup/autotest_runs';local.mkdir(exist_ok=True);out=root/'results/sota_followup/values';out.mkdir(exist_ok=True)
    sid=args.benchmark+'_'+args.corpus+('_smoke' if args.limit else '')
    records=json.loads((root/('data/sota_followup/autotest_input_'+args.benchmark+'.json')).read_text())
    if args.limit:records=records[:args.limit]
    assert all(set(r)=={'position','header','values'} for r in records),'Label/reference fields forbidden'
    df=pd.DataFrame({'header':[r['header'] for r in records],'dist_val':[r['values'] for r in records]},index=[r['position'] for r in records]);df['dist_val_count']=df.dist_val.apply(len)
    os.chdir(source);sys.path.insert(0,str(source));start=time.perf_counter()
    from config import config
    from func import load_corpus
    load_corpus.CORPUS_NAME='labeled_benchmark' if args.benchmark=='rt' else 'excel_benchmark'
    from demo.demo_utils import demo_util
    rules_table=pd.read_csv(source/('results/SDC/'+args.corpus+'_selected_sdc.csv'),sep='\t');rules=[ast.literal_eval(x) for x in rules_table.SDC]
    cache_checks={}
    for kind,folder,suffix in [('sbert','sbert_dist_embedding','dist_val_embeddings.pkl'),('doduo','doduo','dist_val_scores.pickle')]:
        f=Path(config.dir.storage_root_dir)/folder/(load_corpus.CORPUS_NAME+'_'+suffix);cache=pd.read_pickle(f)
        mismatches=[]
        for rid,row in df.iterrows():
            c=cache.loc[rid] if hasattr(cache,'loc') else cache[rid];length=len(c[0]) if kind=='doduo' else len(c)
            if length!=len(row.dist_val):mismatches.append(int(rid))
        if mismatches:raise ValueError('Released feature cache/input cardinality mismatch: '+kind+' '+str(mismatches[:10]))
        cache_checks[kind]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'all_selected_value_counts_equal':True,'cached_columns':len(cache)}
    log=local/(sid+'_native.log')
    with log.open('w') as stream,contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
        results=demo_util.apply_sdc(rules,df)
    lookup={r['position']:{v:i for i,v in enumerate(r['values'])} for r in records};coordinates=[]
    for idx,row in results.iterrows():
        value=row['outlier']
        if value not in lookup[idx]:raise ValueError('Native result outside supplied value universe')
        coordinates.append({'column_position':int(idx),'value_position':lookup[idx][value],'confidence':float(row['conf'])})
    pd.DataFrame(coordinates,columns=['column_position','value_position','confidence']).to_csv(out/(sid+'_autotest_full.csv'),index=False)
    results.to_pickle(local/(sid+'_raw_native_result.pkl'))
    meta={'status':'ORIGINAL_LIMITED','original_pipeline':'author demo_util.apply_sdc; all released SDC families; benchmark precomputed SBERT/Doduo features reused, not freshly recomputed','benchmark':args.benchmark,'corpus':args.corpus,'columns':len(df),'values':int(df.dist_val_count.sum()),'rules':len(rules),'families':dict(collections.Counter(r[1][0] for r in rules)),'cache_checks':cache_checks,'labels_consumed':0,'regime':'U2 external pretrained corpora and published benchmark features; source-table overlap unknown','output':'original one lowest-FPR outlier per column, mapped to actual distinct-value coordinates','alerts':len(coordinates),'wall_seconds':time.perf_counter()-start,'parent_max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'child_max_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'raw_native_log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'raw_native_artifacts':'ignored local files, no restricted data/model redistribution','deviations':['Writable path configuration','Two workers instead of author defaults up to48','Python3.7.16 with pinned compatibility dependencies; original TF/NumPy requirements conflict disclosed','NLTK writable cache path only'],'paper_metric_reproduction':'NOT_CLAIMED: native paper helper mixes column positives with extra outlier negatives; this study uses consistent distinct-value units'}
    (out/(sid+'_autotest_full.json')).write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta),flush=True)

if __name__=='__main__':
    try:main()
    except Exception:
        traceback.print_exc();sys.exit(1)
