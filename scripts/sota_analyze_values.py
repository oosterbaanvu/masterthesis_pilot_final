"""Distinct-value publisher references and occurrence-level transfer cases remain separate."""
import json,os
from pathlib import Path
import numpy as np
import pandas as pd
os.environ.setdefault('MPLCONFIGDIR','/tmp/sota-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sota_followup.value_metrics import evaluate_values
R=Path(__file__).resolve().parents[1];O=R/'results/sota_followup';F=R/'reports/sota_followup/figures';F.mkdir(exist_ok=True);records=[];inventory=[];matched=[]
for name,corpus in [('rt','rt_train'),('st','st_train')]:
    frame=pd.read_csv(O/f'values/{name}_patterns.csv.gz');lookup={p:i for i,p in enumerate(zip(frame.column_position,frame.value_position))};native=json.loads((O/f'values/{name}_{corpus}_autotest_full.json').read_text());assert native['columns']==frame.column_position.nunique()
    for tag,file in [('AutoTest_full',f'{name}_{corpus}_autotest_full.csv'),('AutoTest_pattern_native',f'{name}_pattern_native.csv')]:
        flags=np.zeros(len(frame),bool);confidence=np.zeros(len(frame));output=pd.read_csv(O/'values'/file);assert output.column_position.is_unique
        for row in output.itertuples():
            idx=lookup[(row.column_position,row.value_position)];flags[idx]=True;confidence[idx]=row.confidence
        frame[tag]=flags;frame[tag+'_confidence']=confidence
    methods=['R','RS','riolu_original','riolu_small_sample','lucario_transductive','AutoTest_pattern_only_rt_train','AutoTest_pattern_only_st_train','AutoTest_pattern_native','AutoTest_full'];flags={m:[None if pd.isna(v) else bool(v) for v in frame[m]] for m in methods};scores={m:frame[m+'_confidence'].to_numpy() for m in ['AutoTest_full','AutoTest_pattern_native','AutoTest_pattern_only_rt_train','AutoTest_pattern_only_st_train']};ids=[f'{name}:{c}:{v}' for c,v in zip(frame.column_position,frame.value_position)];truth=frame.publisher_positive.to_numpy(bool);ambiguous=frame.ambiguous.to_numpy(bool)
    metrics=evaluate_values(flags,truth,ambiguous,ids,capacities=(25,50,100),scores=scores)
    # Fractional-budget sensitivity uses the same applicable universe as each matched baseline.
    for method in methods:
        n=sum(v is not None for v in flags[method]);capacities=sorted({max(1,int(np.ceil(n*f))) for f in [.01,.025,.05]})
        for row in evaluate_values({'R':flags['R'],'RS':flags['RS'],method:flags[method]},truth,ambiguous,ids,capacities=capacities,scores=scores):
            if row['method']==method and row['mode']=='budget_union':row['budget_basis']='fraction_of_method_applicable_values';metrics.append(row)
    # Same-pretraining, same native one-outlier reporting policy sensitivity.
    extended=flags.copy();extended['RS']=(frame.RS.astype(bool)|frame.AutoTest_pattern_native.astype(bool)).tolist()
    for row in evaluate_values(extended,truth,ambiguous,ids,capacities=(25,50,100),scores=scores):
        if row['baseline']=='RS' and row['method']=='AutoTest_full':row['baseline']='RS_pretrained_pattern_native';metrics.append(row)
    for row in metrics:
        row.update({'benchmark':name,'unit':'distinct_value','truth_category':'C_PUBLISHER_REFERENCE','regime':'U2' if row['method'].startswith('AutoTest') else 'U0','budget_basis':row.get('budget_basis','fixed_count')})
        if row['mode']=='alone':
            denominator=row['alerts']-row['ambiguous_alerts'];row['publisher_precision_excluding_ambiguous']=row['hits']/denominator if denominator else None
        records.append(row)
    frame.to_csv(O/f'values/{name}_coordinate_outputs.csv.gz',index=False,compression={'method':'gzip','mtime':0});inventory.append({'benchmark':name,'columns':frame.column_position.nunique(),'values':len(frame),'positives':int(truth.sum()),'ambiguous':int(ambiguous.sum()),'original_RIOLU_applicable_columns':frame.loc[frame.riolu_original.notna(),'column_position'].nunique(),'original_RIOLU_applicable_values':int(frame.riolu_original.notna().sum()),'native_full_AutoTest_alerts':int(frame.AutoTest_full.sum()),'RSM':'NOT_APPLICABLE without row context'})
    for cohort,group in [('U0_original_RIOLU_supported',['RS','riolu_original','lucario_transductive']),('U0_small_sample_adaptation',['RS','riolu_small_sample','lucario_transductive']),('U2_same_corpus_native_policy',['RS','AutoTest_pattern_native','AutoTest_full'])]:
        keep=frame[group].notna().all(axis=1).to_numpy();baseline=frame.RS.to_numpy(bool);target=truth&~ambiguous&keep
        for method in group:
            flag=frame[method].fillna(0).to_numpy(bool)&keep;matched.append({'benchmark':name,'cohort':cohort,'method':method,'values':int(keep.sum()),'columns':frame.loc[keep,'column_position'].nunique(),'positives':int(target.sum()),'hits':int((flag&target).sum()),'alerts':int(flag.sum()),'extra_hits_beyond_RS':int((flag&~baseline&target).sum()),'extra_alerts_beyond_RS':int((flag&~baseline).sum())})
df=pd.DataFrame(records);df.to_csv(O/'published_value_metrics.csv',index=False);primary=df[(df['mode']=='alone')&(df.baseline=='RS')&(df.budget_basis=='fixed_count')];primary.to_csv(O/'published_value_primary.csv',index=False);capacity=df[(df['mode']=='budget_union')&(df.baseline.isin(['RS','RS_pretrained_pattern_native']))&(df.capacity==25)&(df.policy=='equal_share')&(df.budget_basis=='fixed_count')];capacity.to_csv(O/'published_value_budget25.csv',index=False)
matched=pd.DataFrame(matched);matched.to_csv(O/'published_matched_cohorts.csv',index=False);fig,axes=plt.subplots(1,3,figsize=(14,4))
for ax,(cohort,group) in zip(axes,matched.groupby('cohort',sort=True)):
    group.pivot(index='method',columns='benchmark',values='hits').plot.bar(ax=ax,fontsize=7);ax.set_title(cohort.replace('_',' '),fontsize=9);ax.set_ylabel('Publisher-positive values retrieved');ax.tick_params(axis='x',rotation=25)
fig.suptitle('Same target universe within each panel; U2 pretraining remains a separate information regime');fig.tight_layout();fig.savefig(F/'published_value_hits.png',dpi=170);fig.savefig(F/'published_value_hits.svg');plt.close(fig)
rows=[]
for p in sorted((O/'pattern_ingest').glob('*.json')):
    d=json.loads(p.read_text())
    for m in d['metrics']:rows.append({**{k:d[k] for k in ['scenario','dataset','family','mechanism','rate','seed']},**m})
p5=pd.DataFrame(rows);p5.to_csv(O/'pattern_ingest_metrics.csv.gz',index=False,compression={'method':'gzip','mtime':0});summary=p5.groupby(['dataset','mechanism','rate','baseline','method','mode','policy','capacity'],dropna=False).agg(cases=('scenario','nunique'),mean_hits=('hits','mean'),mean_extra_hits=('extra_hits','mean'),mean_alerts=('alerts','mean'),mean_extra_alerts=('extra_alerts','mean'),mean_net_hits=('net_hits','mean'),mean_lost_hits=('lost_hits','mean'),mean_newly_triggered_hits=('newly_triggered_reference_hits','mean')).reset_index();summary.to_csv(O/'pattern_ingest_summary.csv',index=False)
(O/'value_analysis_manifest.json').write_text(json.dumps({'publisher_tracks':inventory,'pattern_transfer_scenarios':p5.scenario.nunique(),'pattern_transfer_metric_rows':len(p5),'original_RIOLU_coverage':'default385; small-sample adaptation separately identified','unknown_source_status':'off-transfer occurrence alerts are unknown burden, not true semantic false positives','pretraining_fairness':'U0 matched dirty-input comparisons; U2 full-vs-pattern native ablation; U2-vs-RS is heterogeneous operational increment, not same-information algorithm superiority'},indent=2)+'\n');print(json.dumps(inventory));print(primary[['benchmark','method','eligible_values','reference_positives','hits','alerts','ambiguous_alerts']].to_string(index=False))

# Normalize insignificant SVG line whitespace for reviewable generated artifacts.
for svg in F.glob("*.svg"):
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
