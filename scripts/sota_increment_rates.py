"""Derived rates with explicit references; not real-world semantic precision."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
R=Path(__file__).resolve().parents[1];O=R/'results/sota_followup'
a=pd.read_csv(O/'ingest_metrics.csv.gz');a=a[a['mode']=='union'].copy();a['source_relative_incremental_recall']=a.extra_hits/a.positives;a['source_relative_marginal_precision']=a.extra_hits/a.extra_alerts.replace(0,np.nan);a['meaning']='Recovery of logged source changes; off-change semantic status UNKNOWN';a.to_csv(O/'source_relative_incremental_rates.csv.gz',index=False,compression={'method':'gzip','mtime':0})
rows=[];coverage=[]
for name in ['rt','st']:
 f=pd.read_csv(O/f'values/{name}_coordinate_outputs.csv.gz');truth=f.publisher_positive.to_numpy(bool);amb=f.ambiguous.to_numpy(bool)
 methods=['riolu_original','riolu_small_sample','lucario_transductive','AutoTest_pattern_native','AutoTest_full']
 for method in methods:
  eligible=f[method].notna().to_numpy();d=f[method].fillna(False).to_numpy(bool);coverage.append({'benchmark':name,'method':method,'total_values':len(f),'eligible_values':int(eligible.sum()),'null_values':int((~eligible).sum()),'noncoverage_rate':float((~eligible).mean()),'meaning':'Explicit inapplicability/software/resource exclusions combined; see per-column statuses for causes'})
  for baseline in ['R','RS']:
   b=f[baseline].to_numpy(bool)&eligible;extra=d&~b;known=extra&~amb;positive=truth&~amb&eligible;den=int(positive.sum());rows.append({'benchmark':name,'baseline':baseline,'method':method,'eligible_values':int(eligible.sum()),'reference_positives':den,'baseline_hits':int((b&positive).sum()),'detector_only_hits':int((d&positive).sum()),'overlap_alerts':int((b&d).sum()),'extra_hits':int((extra&positive).sum()),'extra_alerts_including_ambiguous':int(extra.sum()),'extra_ambiguous_alerts':int((extra&amb).sum()),'publisher_relative_incremental_recall':int((extra&positive).sum())/den if den else None,'publisher_relative_marginal_precision_excluding_ambiguous':int((extra&positive).sum())/int(known.sum()) if known.any() else None,'meaning':'Publisher distinct-value reference, not independently adjudicated semantics'})
pd.DataFrame(rows).to_csv(O/'published_reference_increment.csv',index=False);pd.DataFrame(coverage).to_csv(O/'value_method_coverage.csv',index=False);print('Truth-specific marginal rates and explicit noncoverage saved')
