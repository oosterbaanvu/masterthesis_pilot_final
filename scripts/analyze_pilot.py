"""Descriptive analysis, fixed-source group sensitivity, standard exportable plots."""
import collections,gzip,hashlib,io,json,os
from pathlib import Path
import numpy as np
import pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/thesis-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=R/'results/thesis_pilot';P=R/'reports/thesis_pilot';P.mkdir(exist_ok=True);fig=P/'figures';fig.mkdir(exist_ok=True)
rows=[];scenarios=[];failures=[]
for p in sorted((O/'scenarios').glob('*.json')):
 d=json.loads(p.read_text());scenarios.append({k:v for k,v in d.items() if k not in ['metrics','timing']});rows.extend(d['metrics'])
 for f in d['failures']:failures.append(dict(scenario=d['scenario'],dataset=d['dataset'],family=d['family'],**f))
df=pd.DataFrame(rows);df['incremental_recall']=df['additional_hits']/df['changed_cells'];df['net_recall']=df['net_hits']/df['changed_cells'];df['additional_alerts_per_1000_rows']=df['additional_alerts']*1000/800
# Gzip mtime is fixed for reproducible machine-readable output.
buffer=df.to_csv(index=False).encode()
with (O/'all_metrics.csv.gz').open('wb') as file:
 with gzip.GzipFile(fileobj=file,mode='wb',mtime=0) as z:z.write(buffer)
pd.DataFrame(failures).to_csv(O/'method_inapplicabilities.csv',index=False)
keys=['dataset','family','mechanism','rate','baseline','method','mode','budget_per_1000','policy']
summary=df.groupby(keys,dropna=False).agg(scenarios=('scenario','nunique'),mean_hits=('hits','mean'),mean_recall=('change_recall','mean'),mean_extra_hits=('additional_hits','mean'),mean_extra_alerts=('additional_alerts','mean'),mean_incremental_recall=('incremental_recall','mean'),mean_net_hits=('net_hits','mean'),mean_net_recall=('net_recall','mean'),mean_lost_hits=('lost_baseline_hits','mean')).reset_index();summary.to_csv(O/'summary.csv',index=False)

# Conditional within-source duplicate-feature group sensitivity. Neither seeds nor cells
# are treated as independent source datasets. Models/review schedules remain frozen.
groups=json.loads((O/'source_group_metadata.json').read_text());ci=[];rng=np.random.default_rng(20261026)
for name in ['credit','bank','wine']:
 pop=json.loads((O/(name+'_population.json')).read_text());targets=pop['evaluated_targets'];ids=groups[name]['groups'];unique=sorted(set(ids));idx={v:i for i,v in enumerate(unique)};rowg=np.array([idx[x] for x in ids]);n=len(unique)
 for family in ['E4_scale','E5_substitution']:
  subset=[d for d in scenarios if d['dataset']==name and d['family']==family and d['mechanism']=='ECAR' and d['rate']==.05]
  methods=sorted(set.intersection(*[set(np.load(O/'predictions'/(d['scenario']+'.npz')).files) for d in subset])-{'truth','A','B'})
  for method in methods:
   denom=np.zeros(n);gain=np.zeros(n)
   for d in subset:
    z=np.load(O/'predictions'/(d['scenario']+'.npz'));t=z['truth'];extra=z[method]&~z['B'];denom+=np.bincount(rowg,weights=t.sum(axis=1),minlength=n);gain+=np.bincount(rowg,weights=(extra&t).sum(axis=1),minlength=n)
   samples=[]
   for _ in range(400):
    sampled=rng.integers(0,n,n);den=denom[sampled].sum()
    if den:samples.append(gain[sampled].sum()/den)
   ci.append({'dataset':name,'family':family,'method':method,'mechanism':'ECAR','rate':.05,'baseline':'B','incremental_recall':gain.sum()/denom.sum(),'conditional_group_lower':float(np.quantile(samples,.025)),'conditional_group_upper':float(np.quantile(samples,.975)),'groups':n,'interpretation':'Conditional sensitivity of frozen prediction contributions within this source; not confidence for new sources or a test treating seeds as independent.'})
pd.DataFrame(ci).to_csv(O/'conditional_group_sensitivity.csv',index=False)

# Primary tables keep family, source and prevalence separate; binary flags have no fabricated PR-AUC.
main=summary[(summary['mechanism']=='ECAR')&(summary['rate']==.05)&(summary['baseline']=='B')&(summary['mode']=='union')&(summary['family'].isin(['E4_scale','E5_substitution']))]
main.to_csv(O/'primary_alteration_reference_table.csv',index=False)
budget=summary[(summary['mechanism']=='ECAR')&(summary['rate']==.05)&(summary['baseline']=='B')&(summary['mode']=='budget_union')&(summary['budget_per_1000']==25)&(summary['policy']=='equal_share')&(summary['family'].isin(['E4_scale','E5_substitution']))];budget.to_csv(O/'primary_budget_table.csv',index=False)
for family in ['E4_scale','E5_substitution']:
 data=main[main.family==family].pivot(index='dataset',columns='method',values='mean_incremental_recall')
 plt.figure(figsize=(11,3.8));im=plt.imshow(data.to_numpy()*100,aspect='auto',vmin=0,vmax=100,cmap='Blues');plt.xticks(range(len(data.columns)),data.columns,rotation=20,ha='right',fontsize=8);plt.yticks(range(len(data.index)),data.index);plt.colorbar(im,label='Additional altered-cell recall beyond B (percentage points)');plt.title(f'{family}: ECAR, 5%, mean of five paired seeds (exploratory)');plt.tight_layout();plt.savefig(fig/(family+'_increments.png'),dpi=180);plt.savefig(fig/(family+'_increments.svg'));plt.close()
 data=budget[budget.family==family].pivot(index='dataset',columns='method',values='mean_net_recall')
 ax=data.mul(100).plot.bar(figsize=(11,4));ax.axhline(0,color='black',linewidth=.7);ax.set_ylabel('Net altered-cell recall gain (percentage points)');ax.set_title(f'{family}: shared cell-review capacity 25/1000 rows, equal-share policy');ax.legend(fontsize=7,ncol=2);plt.tight_layout();plt.savefig(fig/(family+'_budget_net.png'),dpi=180);plt.close()

# Source-specific mechanism effect at fixed scale and prevalence.
sel=summary[(summary.rate==.05)&(summary.family=='E4_scale')&(summary.baseline=='B')&(summary['mode']=='union')]
fig_,axes=plt.subplots(1,3,figsize=(13,4),sharey=True)
for ax,name in zip(axes,['credit','bank','wine']):
 tab=sel[sel.dataset==name].pivot(index='mechanism',columns='method',values='mean_incremental_recall').reindex(['ECAR','EAR','ENAR']);tab.mul(100).plot(ax=ax,marker='o',legend=False);ax.set_title(name);ax.set_ylabel('Additional alteration recall, pp')
handles,labels=axes[-1].get_legend_handles_labels();fig_.legend(handles,labels,loc='lower center',ncol=3,fontsize=7);fig_.suptitle('Mechanism sensitivity at fixed ×10 transformation and 5% target-column prevalence');fig_.tight_layout(rect=[0,.12,1,.92]);fig_.savefig(fig/'mechanism_sensitivity.png',dpi=180);plt.close(fig_)
status={'scenario_count':len(scenarios),'metric_rows':len(df),'scenario_counts_by_dataset':dict(collections.Counter(x['dataset'] for x in scenarios)),'scenario_counts_by_family':dict(collections.Counter(x['family'] for x in scenarios)),'scenario_counts_by_mechanism':dict(collections.Counter(x['mechanism'] for x in scenarios)),'failure_states':dict(collections.Counter(x['status'] for x in failures)),'metrics_sha256':hashlib.sha256(buffer).hexdigest(),'tables':'Source/family/mechanism/prevalence kept separate; five seeds describe intervention sensitivity, not independent source replication.'}
(O/'analysis_manifest.json').write_text(json.dumps(status,indent=2));print(status);print(main[['dataset','family','method','mean_extra_hits','mean_extra_alerts','mean_incremental_recall']].to_string(index=False));print(budget[['dataset','family','method','mean_net_hits','mean_lost_hits']].to_string(index=False))
