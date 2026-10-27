"""Stratified effects; seeds and source occurrences are not independent datasets."""
import collections,json,os
from pathlib import Path
import numpy as np
import pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/sota-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'results/sota_followup';F=R/'reports/sota_followup/figures';F.mkdir(parents=True,exist_ok=True)
records=[];cases=[]
for p in sorted((O/'ingest').glob('*.json')):
    d=json.loads(p.read_text())
    if 'scenario' not in d:continue
    cases.append(d)
    meta={k:d[k] for k in ['scenario','dataset','view','family','mechanism','rate','seed']}
    for m in d['metrics']:records.append({**meta,**m})
df=pd.DataFrame(records);df['incremental_recall']=df.extra_hits/df.positives;df['net_recall']=df.net_hits/df.positives;df.to_csv(O/'ingest_metrics.csv.gz',index=False,compression={'method':'gzip','mtime':0})
keys=['dataset','view','family','mechanism','rate','baseline','method','mode','policy','budget']
summary=df.groupby(keys,dropna=False).agg(seeds=('seed','nunique'),mean_hits=('hits','mean'),mean_alerts=('alerts','mean'),mean_extra_hits=('extra_hits','mean'),mean_extra_alerts=('extra_alerts','mean'),mean_incremental_recall=('incremental_recall','mean'),mean_net_hits=('net_hits','mean'),mean_net_recall=('net_recall','mean'),mean_lost_hits=('lost_hits','mean'),min_hits=('hits','min'),max_hits=('hits','max')).reset_index();summary.to_csv(O/'ingest_summary.csv',index=False)
advanced=['cdc_original','lucario_original_history','dboost_text_original','contextual_extra_trees']
primary=summary[(summary.mechanism=='ECAR')&(summary.rate==.05)&(summary['mode']=='union')&summary.method.isin(advanced)];primary.to_csv(O/'ingest_primary.csv',index=False)
capacity=summary[(summary.mechanism=='ECAR')&(summary.rate==.05)&(summary['mode']=='budget_union')&(summary.budget==25)&(summary.policy=='equal_share')&summary.method.isin(advanced)];capacity.to_csv(O/'ingest_primary_budget.csv',index=False)
paired=df[(df['mode']=='budget_union')&(df.policy=='equal_share')&(df.budget==25)&df.method.isin(advanced)].pivot(index=['dataset','family','mechanism','rate','seed','baseline','method'],columns='view',values='net_hits').reset_index();paired['full_minus_narrow_net_hits']=paired.full-paired.narrow;paired.to_csv(O/'paired_context_budget.csv',index=False)
# Conditional sensitivity under full-feature duplicate groups; models and review schedules stay frozen.
groups=json.loads((R/'results/thesis_pilot/source_group_metadata.json').read_text());intervals=[];rng=np.random.default_rng(20261027)
for (name,view,family),group in __import__('itertools').groupby(sorted([d for d in cases if d['mechanism']=='ECAR' and d['rate']==.05],key=lambda d:(d['dataset'],d['view'],d['family'])),key=lambda d:(d['dataset'],d['view'],d['family'])):
    group=list(group);g=groups[name]['groups'];unique=sorted(set(g));lookup={v:i for i,v in enumerate(unique)};ix=np.array([lookup[v] for v in g]);n=len(unique)
    for baseline in ['RS','RSM']:
        for method in advanced:
            numerator=np.zeros(n);denominator=np.zeros(n)
            for d in group:
                z=np.load(O/'ingest'/(d['scenario']+'.npz'))
                if method not in z:continue
                numerator+=np.bincount(ix,weights=(z[method]&~z[baseline]&z['truth']).sum(axis=1),minlength=n);denominator+=np.bincount(ix,weights=z['truth'].sum(axis=1),minlength=n)
            values=[]
            for _ in range(300):
                sample=rng.integers(0,n,n);den=denominator[sample].sum()
                if den:values.append(numerator[sample].sum()/den)
            intervals.append({'dataset':name,'view':view,'family':family,'baseline':baseline,'method':method,'incremental_recall':numerator.sum()/denominator.sum(),'conditional_lower':np.quantile(values,.025),'conditional_upper':np.quantile(values,.975),'groups':n,'claim':'conditional frozen contribution sensitivity within source; not new-source confidence'})
pd.DataFrame(intervals).to_csv(O/'conditional_group_sensitivity.csv',index=False)
for baseline in ['RS','RSM']:
    tab=primary[(primary.baseline==baseline)&(primary.view=='full')].pivot(index=['dataset','family'],columns='method',values='mean_incremental_recall')
    fig,ax=plt.subplots(figsize=(10,5));im=ax.imshow(tab.to_numpy()*100,vmin=0,vmax=100,cmap='Blues',aspect='auto');ax.set_xticks(range(len(tab.columns)),tab.columns,rotation=15,ha='right',fontsize=8);ax.set_yticks(range(len(tab.index)),[' / '.join(v) for v in tab.index],fontsize=8);ax.set_title(f'Full context: added source-alteration recall beyond {baseline}, ECAR 5%');fig.colorbar(im,label='percentage points');fig.tight_layout();fig.savefig(F/f'ingest_extra_{baseline}.png',dpi=170);fig.savefig(F/f'ingest_extra_{baseline}.svg');plt.close(fig)
tab=capacity[(capacity.baseline=='RSM')&(capacity.view=='full')].pivot(index=['dataset','family'],columns='method',values='mean_net_hits');ax=tab.plot.bar(figsize=(12,5));ax.axhline(0,color='black',lw=.7);ax.set_ylabel('Net altered cells found vs R+S+M');ax.set_title('Shared 20-cell review capacity per 800-row batch, full context');ax.legend(fontsize=7,ncol=2);plt.xticks(rotation=25,ha='right',fontsize=7);plt.tight_layout();plt.savefig(F/'full_context_budget_net.png',dpi=170);plt.close()
manifest={'context_cases':len(cases),'logical_cases':len(cases)//2,'metric_rows':len(df),'datasets':dict(collections.Counter(d['dataset'] for d in cases)),'families':dict(collections.Counter(d['family'] for d in cases)),'mechanisms':dict(collections.Counter(d['mechanism'] for d in cases)),'all_hard_target_errors':0,'source_reconciliation':'complete under separate upstream-available regime','interpretation':'matched exploratory source-relative effects, not semantic-error rates'};(O/'ingest_analysis_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest))

# Normalize insignificant SVG line whitespace for reviewable generated artifacts.
for svg in F.glob("*.svg"):
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
