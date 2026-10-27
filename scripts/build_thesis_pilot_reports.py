"""Render the executed pilot, with source/family/unit boundaries and explicit limitations."""
import collections,gzip,hashlib,json,os,platform,re
from pathlib import Path
import numpy as np
import pandas as pd
from dq_service.recommend import recommend
from thesis_pilot.data import load,SPECS
from thesis_pilot.controls import Controls
R=Path(__file__).resolve().parents[1];O=R/'results/thesis_pilot';P=R/'reports/thesis_pilot';P.mkdir(exist_ok=True)
def read(p):return json.loads((R/p).read_text())
def report(name,text):(P/name).write_text(text.strip()+'\n')
def table(cols,rows):
 def fmt(v):
  if v is None:return '—'
  if isinstance(v,float):return '—' if np.isnan(v) else f'{v:.3f}'
  return str(v).replace('|','/')
 return '\n'.join(['| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']+['| '+' | '.join(fmt(v) for v in row)+' |' for row in rows])
manifest=read('results/thesis_pilot/analysis_manifest.json');verification=read('evidence/thesis_pilot/independent_verification.json');supp=read('evidence/thesis_pilot/supplement_verification.json')
assert verification['status']==supp['status']=='PASSED'
test_count=int(re.findall(r'(\d+) passed', (R/'evidence/thesis_pilot/all_tests.log').read_text())[-1])
registered=read('results/thesis_pilot/service_registered_intervention.json')
metrics=pd.read_csv(O/'all_metrics.csv.gz');summary=pd.read_csv(O/'summary.csv');main=pd.read_csv(O/'primary_alteration_reference_table.csv');budget=pd.read_csv(O/'primary_budget_table.csv');priority=pd.read_csv(O/'hard_priority_budget_summary.csv')
pops={n:read(f'results/thesis_pilot/{n}_population.json') for n in ['credit','bank','wine']};resources=read('evidence/thesis_pilot/method_resource_profile.json');external={n:read(f'results/thesis_pilot/external/{n}.json') for n in ['hospital','beers']};raha=read('results/thesis_pilot/external/hospital_raha_few_label.json');llm=read('results/thesis_pilot/local_llm/result.json');rows=read('results/thesis_pilot/bank_crossfield_rows/results.json');rich=read('results/thesis_pilot/full_feature_probe/results.json');typed=read('results/thesis_pilot/cdc_type_diagnostic/results.json')
llm_rejected=sum(x['state'].startswith('REJECTED') for x in llm['candidates']);llm_duplicates=sum('DUPLICATE_BASELINE' in x['state'] for x in llm['candidates'])
llm_schema=sum('SCHEMA_CANDIDATE_NOT_EVALUATED' in x['state'] for x in llm['candidates'])
llm_outcome=f"After one prompt-interface repair, {len(llm['candidates'])} schema-only candidates yielded {llm_duplicates} stipulated baseline duplicates and {llm_schema} repetitions of explicit source-schema types, not evaluated as detector additions; {llm_rejected} were rejected. Age's already stipulated bound and unimplemented integer checks were corrected in the semantic validator, preserving its prior classification. The initial four ambiguous candidates and underspecified unary-parameter interface are preserved. No generated rule was promoted or evaluated as an incremental detection benefit."
operational=metrics[(metrics.label_status=='VERIFIED_OPERATIONAL_ERROR')&(metrics.method=='A')&(metrics['mode']=='alone')&(metrics.baseline=='A')]
require=bool((operational.change_recall==1).all());assert require
for baseline in ['A','B']:
 sub=metrics[(metrics.label_status=='VERIFIED_OPERATIONAL_ERROR')&(metrics.method==baseline)&(metrics['mode']=='alone')&(metrics.baseline==baseline)];assert (sub.change_recall==1).all()
full_extra=main[main.method=='cdc_original'][['dataset','family','mean_extra_hits','mean_extra_alerts','mean_incremental_recall']]
example_cdc=main[(main.dataset=='credit')&(main.family=='E5_substitution')&(main.method=='cdc_original')].iloc[0]
example_hits=float(example_cdc['mean_extra_hits']);example_alerts=float(example_cdc['mean_extra_alerts'])
core_table=table(['Source','Family','Detector','Mean additional hits beyond B','Mean additional cell alerts','Added recall'],main[['dataset','family','method','mean_extra_hits','mean_extra_alerts','mean_incremental_recall']].values.tolist())
budget_table=table(['Source','Family','Detector','Net reviewed hits vs B','Lost B hits'],budget[['dataset','family','method','mean_net_hits','mean_lost_hits']].values.tolist())
coverage=verification['method_scenario_coverage'];counts_table=table(['Dataset','Primary scenarios','History rows','Evaluation rows','Evaluated fields'],[(n,manifest['scenario_counts_by_dataset'][n],len(pops[n]['parts']['history']),len(pops[n]['parts']['evaluation']),', '.join(pops[n]['evaluated_targets'])) for n in ['credit','bank','wine']])
primary_claim='Primary results cover four predeclared fields per source, 800 evaluation rows per source and at most 2,400 historical training rows. Full archives were acquired. This is substantial exploratory evidence, not an exhaustive all-field benchmark, a final confirmatory thesis or a production-bank validation.'
label_notice='E1/E2/E3 are verified violations of independently specified operational requiredness/type/domain contracts. E4/E5 are controlled alterations unless a separately stated contract is broken; their recall is alteration recovery, not proven semantic error detection. Unchanged-cell alerts are recorded as unknown/off-change burden, not automatically natural false positives.'
recommendations=[]
for name in pops:
 recommendations.append({'dataset':name,**recommend({'scope':name+' stipulated E1/E2/E3 schema families, evaluated populations only','complete_stipulated_contract_population':True,'baseline_recall':1.,'maximum_additional_verified_hits':0,'external_validity':'No statement about other error families, real bank prevalence or unseen sources.'})})
 recommendations.append({'dataset':name,**recommend({'scope':name+' scale/substitution recovery','reference_kind':'controlled_alterations','target_population_match':False,'external_validity':'Independent semantic correctness and workplace usefulness unestablished.'})})
(O/'recommendations.json').write_text(json.dumps(recommendations,indent=2)+'\n')

report('executive_summary.md',f'''# Executed empirical pilot

**CONDITIONAL GO for a bounded empirical MSc thesis; no operational AI-adoption claim.** Unlike the initial audit, this branch contains executed models and paired experiments. The original audit/manifests/reports remain preserved.

{primary_claim}

{counts_table}

Final primary grid: **630 unique cell-intervention scenarios**, ECAR/EAR/ENAR 210 each; E1 missing 135, E2 datatype 135, E3 code 90, E4 ×10 scale 135, E5 plausible substitution 135. Three prevalence settings (1/5/10% of the eligible target column), five seeds. There are **52,740 metric rows**, not 52,740 independent experiments. A separate **45-scenario Bank cross-field row track**, **18 full-feature scope probes**, **18 source-type CDC diagnostics**, two published-reference tables and eight synthetic linked-table cases were executed.

Main findings:

- Basic and extended controls detect every injected stipulated E1/E2/E3 violation in the 360 relevant primary scenarios. No detector can add unconstrained true hits beyond this complete coverage for these narrowly defined families.
- CDC's native configuration sometimes adds substantial **alteration-reference hits**, with high extra alert burden. For ECAR at 5%, Credit substitution adds {example_hits:.1f}/40 changed cells on average beyond B, but {example_alerts:,.1f} extra cell alerts per 800-row batch. Those are matched altered values, not newly proven semantic data errors.
- At a shared review capacity, gains can shrink or become negative. Control priority and fusion policy matter. A provenance-based hard-rule-priority sensitivity is reported separately from the predeclared binary-hash policy.
- Original LUCARIO including regex inference was reproduced, with exact 20,000-cell flag parity on the authors' Hospital example. Original CDC, original dBoost, a separately named ExtraTrees predictor and original Raha learning stages were executed. Raha receives 20 labelled rows and is never pooled with label-free methods.
- Publisher-reference tests can show complementary hits, but Hospital's x-substitution signature and Beers' representation changes prevent general natural-error claims.
- Local Qwen3-0.6B Q8_0 ran locally. {llm_outcome}

Verification: **{test_count} tests passed in the pilot environment**, {sum(verification['checks'].values()):,} primary independent arithmetic/identity checks, and {supp['total_assertions']:,} supplemental checks. This is independent software implementation, not independent human semantic adjudication. Original lightweight audit environment separately passes 29 tests with the new optional pilot module skipped.

Engineering: dataset registration, source hashing, contracts, A/B rules, four selectable detector adapters, findings and bounded recommendations execute locally. A generic registered-source intervention command also executes on a copy: {registered['realized_changes']} verified type violations, original source unchanged. The synthetic demonstration finds its two existing known schema violations; the source scan returns INSUFFICIENT_EVIDENCE without real labels. See [final recommendation](final_recommendation.md).
''')
report('research_design.md',f'''# Research design and frozen exploratory protocol

Working RQ: To what extent do learned/statistical error detectors add detection beyond conventional controls, and how does this depend on error family, mechanism, baseline strength and review capacity? The essential comparison is B+detector versus B, not detector recall in isolation. Negative and negligible gains are valid outcomes.

{primary_claim}

Primary protocol: `configs/thesis_pilot/protocol_v1.json` v1.3. Initial engineering smoke, the complete v1.1 grid and subsequent corrections are preserved under `results/thesis_pilot/attempts/` and `evidence/thesis_pilot/protocol_amendments.json`. v1.2 corrected CDC missing-input eligibility and seeded LUCARIO. A further direct audit found known full-feature duplicates spanning the internal Wine fit/calibration split. v1.3 retains one representative per known full-feature history group, with all original evaluation rows and operations unchanged, then reruns all 630 scenarios and affected diagnostics. Original v1.1/v1.2 outputs remain preserved. No source, transformation, threshold or model was selected for favourable outcomes.

Splitting uses **exact feature-vector duplicate groups within each source**, excluding prediction outcomes and Credit ID. Groups are assigned by a fixed hash to history/development/evaluation/reserved portions; history/evaluation are capped at 2,400/800 rows; one representative per full-feature history group is retained before internal model/calibration splits. This avoids the observed known-duplicate crossing (154 Wine groups in the former fixed fit/calibration split). It changes reference frequency weighting and is an explicit preprocessing choice, not evidence that history is clean. This is not source-table independence, customer-identity resolution or a chronological delivery design. The original Bank file's temporal order is not claimed as an operational forecast. All historical public sources are exploratory. The reserved groups were excluded from model fitting/intervention evaluation; prior whole-source audits mean they are not pristine unseen sources.

Hypotheses: incremental hits can be zero; credible stronger controls can eliminate apparent gains; shared capacity can make extra alerts harmful; placement effects can differ even at the same relative corruption magnitude. Mechanism diversity is a sensitivity factor, not revival of the earlier detector-selection objective.

{label_notice}

Native methods see the same allowed historical values and the current corrupted batch, without evaluation labels, original clean references or outcome fields. CDC additionally relies on a presumed usable reference/calibration population: original history is not independently certified clean, and conformal guarantees are not asserted. LUCARIO history fitting is an explicit information-regime adaptation of its native per-column inference/application; transductive author-style examples and external validation are reported separately. Raha gets metered reference labels in an explicitly separate regime.

Comparisons: A, B, each applicable detector, A+detector and B+detector. Native flags remain binary. No fake confidence ranking or PR-AUC is invented. Default order is a fixed SHA-256 of row identity and target column; control_first and equal_share fusion are fixed. Primary review units are cells at 10/25/50 cell reviews per 1,000 batch rows. There are four evaluated columns per row. The separate E6 process uses row reviews, never pooled with cell metrics.

Report both unconstrained unions and fixed total capacity, including missed/displaced baseline hits. Untouched predictions identify whether an affected cell was already flagged. Zero extra alerts have undefined marginal precision. Primary tables keep source, family, mechanism and prevalence separate.

Uncertainty: five seeds describe placement variability on fixed sources. Conditional duplicate-feature-group resampling of frozen prediction contributions is saved in `conditional_group_sensitivity.csv`. Those intervals do not establish customer/source independence, new-source confidence or a seed-based significance claim. Full source identifiers and real longitudinal entities are unavailable. No final hypothesis test is claimed.

Post hoc but separately declared diagnostics: 18 all-input-feature probes, 18 source-declared CDC type probes, hard-control provenance priority, and 45 Bank row-relation scenarios with their own pre-intervention contract. They do not silently replace the primary native configurations.
''')
report('dataset_qualification.md',f'''# Dataset qualification by evaluation track

Primary intervention sources are fully acquired: Credit (30,000 × 25 raw fields including ID/outcome), Bank additional full (41,188 × 21) and White Wine (4,898 × 12). Archive/member identities, immutable byte hashes and UCI source URLs are in `manifests/thesis_pilot/datasets.json`. UCI pages describe CC BY 4.0; attribution remains required. Original bytes are unchanged and ignored. Prediction outcomes default-payment/y/quality and Credit ID are excluded from model features and error labels.

{counts_table}

These sources pass acquisition, shape, duplicate-group separation and **track-specific intervention** checks. None is certified globally clean. Unknown source anomalies are not manufactured negatives. Permissive Credit category contracts preserve the known undocumented/exceptional education/marriage/payment codes; those observed exceptions are not declared naturally erroneous. Bank `unknown` and `pdays=999` remain legitimate source conventions. No unsupported rule declares all `pdays=999` rows to have previous=0. Wine concentrations and percentage/pH bounds are explicit operational stipulations, not all copied as publisher-provided business rules.

The primary four-column views support a coherent common unit, but do not exhaust all available cross-field information. The separately executed full-feature probes supply all 23/20/11 non-outcome input fields to both the conditional baseline and contextual models, retaining the same four scored fields. They are sensitivity evidence, not additional datasets.

External Hospital and Beers were executed on publisher-reference differences. Hospital/Raha and HoloClean variants are related, not independent replications. Flights remains a conditional multi-source/entity-keyed candidate; it was not silently scored with incompatible row references. RT/ST remain distinct-column/value benchmarks with the original audit's 1,194/1,193 eligible columns. No relational rows or occurrence counts were invented. Full Auto-Test inference was not reproduced. REIN's primary external files remained access-limited; its paper is now acquired and reviewed through arXiv:2302.04702v1.

Synthetic accounts/transactions/ledger/reference relationships are engineering fixtures only. Their eight mutations test stipulated contracts; they do not add a fourth independent real source or support real financial prevalence/generalisation claims.
''')
report('rule_baselines.md',f'''# Rule baseline provenance and applicability

A/B configurations and per-column provenance: `results/thesis_pilot/*_contracts.json`. The separate `manifests/thesis_pilot/rule_provenance.json` enumerates each applied primary control, its own provenance, parameters and evidence; this separates stipulated requiredness from documented categorical domains. A is not intentionally weakened. Every evaluated cell has an explicit operational requiredness and datatype/category contract. B includes all A findings; the code and tests assert A ⊆ B for unconstrained alert sets.

| Layer | Controls | Provenance and limits |
| --- | --- | --- |
| A | Explicit requiredness; finite numeric parsing; accepted category codes; justified/stipulated physical bounds | Requiredness generally EXPLICIT_STIPULATED_CONTRACT. Bank category lists DOCUMENTED_SOURCE_CONTRACT. Credit code acceptance is deliberately permissive. Wine bounds use an explicit operational convention. |
| B | A plus 0.5/99.5% history quantiles, 3-IQR robust bounds, category-share threshold 0.005, conditional Ridge residual threshold calibrated on the last quarter of history | TRAINING_ONLY_STATISTICAL_CONTROL, not semantic business truth. Ridge α=10 and thresholds are frozen independently of evaluation interventions. |
| Row E6 | previous=0 iff poutcome=nonexistent, with lexical/domain controls and statistical row alerts | EXPLICIT_STIPULATED_CONTRACT motivated by Bank campaign semantics; verified on untouched approved rows before mutation. Findings are rows, not blame assigned to every participating cell. |
| Linked-table fixture | Unique IDs, parent references, status enum, integer cents, expected deliveries, debit/credit and source/ledger totals | EXPLICIT_STIPULATED_CONTRACT on explicitly synthetic data. |

Conditional linear residual monitoring makes B broader than univariate thresholds. It is still a research approximation of available conventional controls, not a certified mature bank suite. Single-source UCI tables do not contain account/transaction parents or legitimate ledger totals: those checks are NOT_APPLICABLE in the primary cell track and executed in the linked fixture instead. The full Bank relation is evaluated in its separate row track. No dependency is invented from correlation alone.

Numeric lexical validity is checked before bounds; INVALID_NUMERIC and NaN cannot silently bypass range rules. IDs/postcodes/phone strings are never generically normalised as numbers in external data. Statistical preprocessing of numeric model features can impute unparseable values, but this is explicit; the ExtraTrees residual adapter abstains on an invalid numeric target rather than claiming to infer its semantic correctness.

Budget policies matter: adding statistical alerts increases the unconstrained superset but can consume review capacity. The primary binary-hash policy remains reported. `review_priority_sensitivity.json` separately puts A's hard-contract alerts before B's statistical suspicion, then combines remaining candidates without test-label priority. This is a post hoc provenance-policy sensitivity, not retrospective threshold tuning.
''')
report('injection_validation.md',f'''# Executed intervention validation

630 final primary scenarios; {manifest['scenario_counts_by_mechanism']}. Counts by family: {manifest['scenario_counts_by_family']}. The 1/5/10% denominator is **eligible rows in the selected target column**, not every cell of the table. Exact intended/realised counts, eligibility, rank diagnostics and seeds are saved in `injection_validation.csv` and every scenario JSON. Source-specific zero amounts are excluded from scaling; rates are therefore not assumed to have identical raw counts across sources.

Operations: E1 empty required value; E2 invalid numeric lexical token; E3 explicit out-of-domain code (Credit/Bank only; Wine NOT_APPLICABLE); E4 ×10 nonzero values; E5 another plausible original value from the same column. No-op changes are rejected. E4/E5 remain alteration targets; source consistency/physical validity is not assumed broken merely because a value changed.

Placement delegates to pinned official **tab_err 0.2.2** source revision `4e5d348e442824f3c09ed462e37dbbe910ef330a`. That revision is not on PyPI under 0.2.2, so the package is installed from the verified Git source. ECAR is uniform without replacement. EAR selects a random contiguous block of rows sorted by another original field; ENAR uses the original target field. These are the authors' hard-window mechanisms, not the earlier pilots' soft rank-weighted samplers.

The independent verifier reconstructs each chosen location directly from NumPy RNG and original source values, without importing tab_err or the production injector. A separate 80-seed synthetic check verifies ECAR mean-rank behaviour, and EAR/ENAR selected rank spans are checked on a tie-free fixture. Actual data can contain tied categories and correlated fields: a categorical ENAR window imposes an ordering and does not establish a meaningful ordinal business mechanism. Random window position is itself a seed effect.

Within a matched source/family/seed, the replacement for the same row is identical across mechanisms/rates. E4 relative severity is always ×10. Absolute differences and donor recovery difficulty can still change when different original values are selected; that is reported as population/placement sensitivity rather than concealed as identical absolute severity. The supplemental checker validates matched counts and per-row transformation identity.

Original values/new values and source-row coordinates are kept in ignored `data/pilot_runs/*.json`, each hash recorded in committed scenario metadata. Predictions, truth masks and metric outputs are committed; raw original datasets and fitted weights are not. Replay reconstructs the exact injected values from source hashes and seeds.

Untouched batches are scored before interventions. Already-flagged changed cells are not labelled newly triggered. E5 supplies an explicit validity-preserving/unknown-semantic negative-control population. E6 adds 45 separately labelled Bank row-contract scenarios; scarce positive-previous eligibility uses a documented minimum of one mutation, so realised rates can exceed nominal tiny percentages. E7/E8 key/foreign-key/reconciliation cases execute on the synthetic fixture, never imaginary UCI joins.
''')
method_rows=[]
for method,n in coverage.items():
 if method in ['A','B']:continue
 method_rows.append((method,n,'original configured source' if method!='contextual_extra_trees' else 'own explicitly named adaptation', 'cell flags; no fabricated ranking'))
resource_table=table(['Method','Fit sec','Untouched score sec','Measured RSS MiB'],[(x['method'],x.get('fit_seconds'),x.get('score_seconds'),x.get('rss_high_water_kib',0)/1024) for x in resources])
report('detector_reproduction.md',f'''# Detector reproduction, fidelity and information access

Source revisions/rights: `configs/thesis_pilot/sources.json`. Exact package environments: `envs/thesis_pilot/*.lock.txt`. The original source code stays in ignored caches; no LUCARIO or ZeroED source licence is invented. LUCARIO's top-level code licence remains unlocated, so local execution is conditional and its source is not redistributed. The author paper DOI metadata/abstract explicitly names LUCARIO; the final title is *Unsupervised, robust, and lightweight detection of data pattern anomalies and outliers*, DOI 10.1016/j.infsof.2026.108035, differing from the repository's preliminary title. Full paper PDF was not retrieved here; code and author-example evidence must not be called full-paper score reproduction.

{table(['Primary configuration','Scenarios scored','Implementation','Output'],method_rows)}

- **dBoost:** actual original Pearson analyzer + Gaussian model, threshold 3, correlation 0.5. Text mode uses original API on explicit string tuples; numeric mode uses explicit numeric floats and string categories. The row-dropping CSV reader is bypassed. Neither multiple encodings nor multiple parameters count as independent algorithm families. Missing/invalid numeric scenarios are inapplicable for the numeric mode (270), not silently dropped rows or assigned zero performance. The mixed-period full Bank probe succeeded; a legitimate 20-row homogeneous Bank-period history reproduced the float fractional-part cancellation failure. A separately named cached stable-population-moment compatibility worker passed the same input and centred-variance tests. It did not replace primary original-code predictions.
- **LUCARIO:** complete original type, categorical range, numeric MAD and regex/pattern inference classes execute. The application adapter matches all **20,000** author Hospital flags exactly after running both author scripts (only dataset-list selection parameterised). History fitting is an explicit regime adaptation; external tests use the current unlabelled table transductively. Original numeric range switch-off at >5% flagged is retained and documented. 10% operational contamination challenges its 95%-healthy assumption. KMeans is seeded with 42; author parity is a single-fixture check, not proof across all domains.
- **CDC:** original `ConformalAutoGluonCleaner` and pinned `conformal-inference` cleaning-paper source, Python 3.9, AutoGluon 0.8.2. Supported compute-limited RF/XT portfolio, 40 trees each, one HPO trial, confidence .95, calibration fraction .25. This reproduces the released algorithm pipeline, not the paper's full AutoML search or published scores. Original automatic dtype guessing and boundary behaviour are retained in primary outputs. No independent clean-history or exchangeability guarantee is asserted. Invalid lexical numeric input is inapplicable (135); missing numeric input is supported and produces the native outlier-mask semantics (already-missing targets are excluded). The corrected eligibility triggered a complete rerun with old evidence preserved. **18 source-type diagnostics** separately override only inferred source types; they do not inherit original automatic-inference fidelity claims or prove semantic truth.
- **Contextual ExtraTrees:** own adapter, 64 trees, depth 16, leaf size 5, fixed seed 42. Per-column prediction from other permitted fields; residual or class-probability threshold calibrated at .995 on held historical values. This is not CDC or another published detector implementation, and is not a new algorithm contribution. Unparseable target cells are explicitly counted as abstentions; their flags are not invented.
- **Raha:** original strategy, feature, clustering, label propagation and GBC prediction stages, OD/PVD/RVD with KBVD disabled through its supported configuration. {raha['strategy_count']} strategies, 20 publisher-labelled rows / {raha['annotation_cells']} cells. No clean_path reaches the method; bulk reference retrieval is guarded, and queried rows are excluded from evaluation. This is a separately named few-label ablation, not label-free competition or independent human annotation.
- **Auto-Test:** paper/SDC resources reviewed. Actual inference entrypoint attempts and lightweight dependency repairs are logged; the full legacy model/embedding/pickle environment was not reproduced. No partial SDC subset is called full Auto-Test and no zero score is invented.
- **ZeroED:** original paper and official source acquired. Actual entrypoint import failed on fasttext; additional missing measure module, external embeddings and large-model pseudo-label pipeline were inspected. Full original pipeline was NOT_EXECUTED. The local Qwen rule demo is not relabelled ZeroED or a reproduction of its Qwen2.5-72B results.

{resource_table}

RSS measurements are representative Credit workloads and include interpreter/library overhead; parent versus worker scopes are explicit in the machine-readable profile. They are not full-grid peak-memory claims. Per-scenario timings and fit times were recorded under shared capped CPU resources, not a controlled microbenchmark.
''')
example=[]
for label,baseline,method,mode in [('A','A','A','alone'),('B','B','B','alone'),('CDC alone','B','cdc_original','alone'),('A + CDC','A','cdc_original','union'),('B + CDC','B','cdc_original','union')]:
 x=summary[(summary.dataset=='credit')&(summary.family=='E5_substitution')&(summary.mechanism=='ECAR')&(summary.rate==.05)&(summary.baseline==baseline)&(summary.method==method)&(summary['mode']==mode)]
 assert len(x)==1
 row=x.iloc[0];example.append((label,row['mean_hits'],float(metrics[(metrics.dataset=='credit')&(metrics.family=='E5_substitution')&(metrics.mechanism=='ECAR')&(metrics.rate==.05)&(metrics.baseline==baseline)&(metrics.method==method)&(metrics['mode']==mode)]['alerts'].mean())))
example_table=table(['Configuration, Credit substitution ECAR 5%','Mean recovered changed cells / 40','Mean total cell alerts / batch'],example)

report('experimental_results.md',f'''# Actual primary comparisons

**630 scenarios; 52,740 metric rows.** Raw machine-readable metrics: `results/thesis_pilot/all_metrics.csv.gz`; source/family/mechanism/rate/seed and applicability are retained. Prediction matrices are in `predictions/`; every scenario JSON pins their hash and the complete local injection log. No model ranking is inferred from unequal populations.

Operational E1/E2/E3: in all **360** applicable scenarios, both A and B have unconstrained recall 1.0 on the stipulated violations; additional verified hits beyond either complete control set are zero. These are functional ceiling/sanity results, not proof that all real data errors are covered.

A concrete A/B/detector/combination comparison (controlled changes, not semantic truth):

{example_table}

The table below is **ECAR, 5% eligible target-column prevalence**, mean of five paired seeds. Hits concern controlled scale/substitution changes. Alerts are additional cell reviews per 800-row, four-target-column batch. Do not read these as natural semantic-error precision or production costs.

{core_table}

Shared capacity: **25 cell reviews per 1,000 batch rows**, so 20 reviews for an 800-row batch. The following is the predeclared equal-share binary policy, net reviewed altered-cell hits relative to the same B capacity. Negative values are preserved. A method can alter which already-flagged B candidates get reviewed; budget gains are not necessarily new unconstrained detections.

{budget_table}

Other percentages, mechanisms, baseline A and control-first policies are in `summary.csv`. `hard_priority_budget_summary.csv` repeats capacity evaluation with independently justified hard-contract priority; this post hoc policy sensitivity is not pooled into the predeclared result. Source/family strata remain distinct. Native numeric dBoost and CDC are absent where input domains are unsupported; missing execution is not zero performance.

![Scale increments](figures/E4_scale_increments.png)
![Substitution increments](figures/E5_substitution_increments.png)
![Shared-capacity scale effects](figures/E4_scale_budget_net.png)
![Mechanism sensitivity](figures/mechanism_sensitivity.png)

Separate executed follow-ups: 18 all-feature probes, 18 source-type CDC probes and 45 Bank row-contract scenarios. The probes retain the same source splits and labels, are explicitly exploratory, and are not counted as independent new sources. The row experiment demonstrates a valid cross-field invariant: B detects each stipulated row violation; it never pretends to identify every wrong participant cell. See their JSON/NPZ outputs and the independent supplemental checks.
''')
ext_rows=[]
for name,meta in external.items():
 for x in meta['outcomes']:
  if x['baseline']=='B':ext_rows.append((name,x['method'],x['reference_hits'],x['alerts'],x['additional_reference_hits'],x['additional_alerts'],x['marginal_reference_precision']))
report('external_validation.md',f'''# Executed publisher-reference validation

Track state: **EXECUTED_CONDITIONAL**. Hospital and Beers use exact pinned raw reference disagreements with explicit schema correspondence and identity-column exclusions. Both native LUCARIO and dBoost-text receive the same unlabelled current table; no clean values configure their fit. A is a generic missing-token screen; B adds generic unlabelled profiling. This is not a certified mature source-specific enterprise baseline and is not claimed as one.

{table(['Source','Method','Own reference hits','Own alerts','Extra reference hits beyond B','Extra alerts','Marginal reference precision'],ext_rows)}

Hospital has 509 raw differences; 508 exhibit the x-substitution signature. Beers has 4,362 raw differences, including unit/representation and missing-token changes. These outcomes measure **publisher-reference agreement**, not independently verified natural semantic errors. Reference-consistent cells can contain unknown defects. Therefore the numerical precision columns are reference-relative only. Entire original/clean files remain unchanged. Source variants are not counted as independent datasets.

Original Raha OD/PVD/RVD ablation, separate information regime: 20 labelled rows ({raha['annotation_cells']} cell judgements simulated from publisher labels), excluded from scoring. It records {raha['reference_hits']} reference hits, {raha['alerts']} alerts and {raha['positives']} remaining positive reference cells; reference precision {raha['reference_precision']:.3f}, recall {raha['reference_recall']:.3f}. Annotation cost and supervision prevent a single leaderboard with label-free models. No human was simulated as having actually annotated anything.

Flights' entity/reference lineage, RT/ST distinct-value granularity and unreproduced complete Auto-Test runtime remain separate limitations. No imaginary joint rows, cell frequencies or compatible-looking scores were fabricated. REIN full dataset access failure is preserved, and the original REIN paper is now reviewed; UCI sources were never substituted as naturally labelled REIN data.
''')
neg=metrics[(metrics['mode']=='budget_union')&(metrics.net_hits<0)]
report('incremental_value_analysis.md',f'''# Incremental value and review burden

The investigation distinguishes new unconstrained hits, review selection, already-present alerts and semantic correctness. Source-specific tables are the evidence; no synthetic/natural/column-value pooled F1 is reported.

1. **Closed operational schema families:** A already detects all stipulated E1/E2/E3 violations. More unconstrained detection is mathematically impossible within that target; combining a learned detector mainly adds burden. This says nothing about undocumented real errors.
2. **Alteration recovery:** a model can add many reference hits while sending hundreds of extra alerts. Example: native CDC on Credit ECAR 5% substitution adds {example_hits:.1f} changed-cell hits, with {example_alerts:,.1f} extra alerts per batch. These cannot be called extra independently verified semantic data errors. Its automatic numeric-to-categorical inference and rare/tied calibration behaviour require attention.
3. **Shared total capacity:** there are {len(neg):,} negative net-hit metric rows under the predeclared policies. These rows are repeated conditions on fixed sources, not independent negative discoveries. Baseline strength, fusion policy and relative alert volume explain why union recall alone can mislead.
4. **Control maturity includes priority:** provenance-based hard-contract priority is a separate, justified sensitivity. The order is chosen from control category, not held-out labels. It prevents statistical suspicion from arbitrarily displacing known hard failures before capacity is shared. The original binary-hash policy remains visible.
5. **Information and model fidelity:** text/numeric dBoost are one family; history-fitted LUCARIO is not its transductive author benchmark; CDC native types differ from source-declared numeric semantics; the ExtraTrees predictor is an explicit adaptation. Raha and local LLM knowledge have additional information and remain separate.
6. **Mechanisms:** fixed relative ×10 severity and matched counts do not guarantee equal absolute difficulty. EAR/ENAR's hard-window position, source correlations and tied category order change selected populations. The full mechanism tables, not a cross-source global mean, support interpretation.

`conditional_group_sensitivity.csv` resamples exact-feature duplicate groups **within each fixed source**, with predictions and review decisions frozen. These are conditional sensitivity intervals, not new-source confidence intervals, independent customer inference or significance from five seeds. No measured human handling time exists, so operational money saved and cost per genuinely useful semantic detection are NOT_ESTIMATED. Runtime and count-based review burden are measured.

The bounded recommendation is DO_NOT_ADOPT a detector solely to add coverage for already complete stipulated schema families; for plausible changes and operational deployment, INSUFFICIENT_EVIDENCE. No universal rejection or adoption of AI follows from these examples.
''')
issues=[
('T01','technical','uv cache read-only / unavailable PyPI tab_err 0.2.2','Workspace cache; pinned official source installation','RESOLVED_VERIFIED','pilot_install_source.log, reusable_setup_test.log'),
('T02','technical','CDC Python/AutoGluon compatibility','Separate Python 3.9 plus exact author CI source and supported RF/XT budget','RESOLVED_VERIFIED','cdc_install.log, *_cdc_original_fit.json'),
('T03','methodological','Prior LUCARIO-core omitted regex inference','Execute all original inference classes and both author scripts; exact flag parity','RESOLVED_VERIFIED','lucario_authors_parity.json'),
('T04','technical','One-pass float variance cancellation in native dBoost','Mixed-period probe succeeds; homogeneous real Bank-period failure reproduced, stable cached population moments retested without clipping or dropping inputs','RESOLVED_VERIFIED','dboost_period_retest.json, dboost_numeric_diagnosis.json'),
('T05','technical','First stable moment attempt exceeded time limit by recomputing moments per query','Cache exact moment values and invalidate cache on update; complete failing-input retest','RESOLVED_VERIFIED','dboost_stable_attempt1_timeout.log, all_tests.log'),
('T06','methodological','CDC missing numeric input wrongly excluded','Original input probe proves support; preserve native missing-mask semantics; rerun all 630 scenarios','RESOLVED_VERIFIED','cdc_missing_probe.json, protocol_amendments.json'),
('T07','technical','Original LUCARIO KMeans unseeded','Seed 42, preserve old outputs, rerun main and external outputs','RESOLVED_VERIFIED','protocol_amendments.json'),
('T08','domain','Native CDC may infer numerical amounts/ages as categorical; native boundary/rare-class effects','Retain primary native behaviour and execute 18 source-declared-type diagnostics; no theoretical guarantee or replacement of originals claimed','RESOLVED_CONDITIONALLY','cdc_type_diagnostic/results.json'),
('T09','methodological','Shared capacity can prioritise statistical suspicion before hard contract failures','Separate post hoc provenance-priority sensitivity, without test-label ordering or retuning models','RESOLVED_CONDITIONALLY','hard_priority_budget_results.csv'),
('T10','technical','llama-cli target unavailable in current build layout; model redirect denied','Use actual llama-completion target and specific public CDN allowlist; verify checkpoint against publisher LFS checksum','RESOLVED_VERIFIED','llama_completion_build.log, local_model_acquisition.json'),
('T11','scientific','LLM valid JSON contains ambiguous parameters; prompt omitted unary-parameter convention; validator omitted stipulated age bound and overstated integer checks as baseline duplicates','Preserve initial four rejected outputs; specify empty unary values and retry once without labels. Validate against actual frozen controls: two bound duplicates and two schema repetitions without detector evaluation. Preserve prior classification; no automatic promotion.','RESOLVED_VERIFIED','local_llm/result.json, attempts/local_llm_initial_ambiguous_interface'),
('T12','technical/licensing','Complete Auto-Test/ZeroED environments, artifacts and rights not qualified','Bounded code/paper and execution attempts, no approximate scores or paid inference; continue all other tracks','BLOCKED_TECHNICAL','optional_attempts.json, autotest_retry_after_dependencies.json'),
('T13','scientific','Published reference disagreement is not independent semantic truth','Keep reference-relative labels/metrics; no invented human annotation; separate from intervention tracks','INTRINSIC_LIMITATION','external_validation.md'),
('T15','technical/methodological','Known full-feature duplicates crossed the internal reference fit/calibration split (154 Wine groups)','Retain one original full-feature representative per approved history group, prove history uniqueness independently, preserve v1.2 and rerun all affected comparisons','RESOLVED_VERIFIED','inner_calibration_group_audit.json, protocol_amendments.json, independent_verification.json'),
('T14','scientific','Exact duplicate groups are not independent sources or known clients','Correct interpretation explicitly; conditional within-source sensitivity only; no seed-based source significance','INTRINSIC_LIMITATION','research_design.md, source_group_metadata.json')]
issue_records=[dict(zip(['id','root_cause_type','root_cause','repair','status','evidence'],x)) for x in issues]
(R/'manifests/thesis_pilot/issues.json').write_text(json.dumps(issue_records,indent=2)+'\n')
report('domain_issues_and_repairs.md','# Domain/technical repair and retest register\n\n'+table(['ID','Cause','Repair','Status','Evidence'],[(x[0],x[2],x[3],x[4],x[5]) for x in issues])+'''\n\nAll changes are versioned; v1.1 results and earlier smoke outputs remain in attempts/. The final primary results are v1.3, independently recounted after duplicate-reference correction. Repairs did not select favourable labels, remove hard cases or silently rename an approximation as an original method. Native constraints containing source values are preserved locally under ignored data/pilot_models; committed metadata contains summaries/checksums. No unpublished source licence or human review is invented.\n''')
report('literature_and_novelty.md','''# Closest literature and bounded novelty assessment

The practical motivation from Long Tran concerns existing schema, business, referential, reconciliation and monitoring controls. Dashboards/manual exception handling are workflows, not extra detection algorithms. This pilot evaluates rule/statistical findings, not whether a dashboard exists. No claim is made that Long or university supervisors have approved this precise thesis design.

| Work | Original evidence examined | Consequence |
| --- | --- | --- |
| Abedjan et al., *Detecting Data Errors: Where are we and what needs to be done?*, PVLDB 2016 | Official full text already acquired, especially combination/configuration analysis | Complementarity is established prior work; ground-truth-informed configuration cannot be copied as held-out tuning. |
| Pit-Claudel et al., dBoost, MIT-CSAIL-TR-2016-002 | Original source/paper TeX, native execution and float failure/retest | Statistical tuple expansion is one family, not two AI methods merely because encodings differ. |
| Mahdavi et al., Raha, SIGMOD 2019, DOI 10.1145/3299869.3324956 | Author paper/code and real metered-label execution | Supervision/annotation budget fundamentally changes information access. |
| Jäger & Biessmann, CDC, AISTATS 2024, PMLR 238:3394–3402 | Official full text, original cleaner and CI source, actual AutoGluon execution | Clean-history/calibration assumptions and native output decisions must remain explicit; not a generic dirty-data guarantee. |
| Chen et al., Auto-Test, arXiv:2504.10762v1 / PACMMOD 2025 | Official full text §6.1 and complementarity experiments, actual released CSV audit | Additional constraints/errors beyond existing constraints are already demonstrated. Do not claim “AI plus rules” is novel. |
| Abdelaal, Hammacher & Schöning, REIN, arXiv:2302.04702v1 | Original full text now acquired and inspected, plus source | Broad detector/repair combinations and heterogeneity are already studied. The original audit's missing-paper limitation is partly closed; dataset access remains separate. |
| Jung et al., tab_err / Towards Realistic Error Models for Tabular Data | Exact official 0.2.2 source and mechanism behaviour independently verified; publication metadata DOI 10.1145/3774914 | What changes and where changes occur are distinct; do not rename soft rank sampling as author hard-window ECAR/EAR/ENAR. |
| Qin et al., LUCARIO, DOI 10.1016/j.infsof.2026.108035 | Published metadata/abstract and full original code; exact author-example parity | Full regex inference now executes. Full article PDF was not retrieved; no full-paper metric reproduction is claimed. |
| Ni et al., ZeroED, arXiv:2504.05345 | Original paper and official source/configuration | LLM-generated criteria, pseudo-labels and propagation are not reproduced by a standalone small local rule generator. |

A plausible contribution is a carefully bounded **empirical account of baseline strength, valid error/alteration targets, permitted information and total review capacity**. Mechanism sensitivity is secondary, not a claim that mechanism-diverse detector selection succeeds. Independent label and information accounting may make negative findings informative, but this combination's novelty is **not yet established**. Additional forward/backward citation review and supervisor agreement are required before a confirmatory thesis contribution is asserted.

Earlier repositories were inspected read-only. Their conclusions were not copied as new results. This branch now has new executions, complete LUCARIO inference, native CDC execution, explicit hard-window mechanisms and separate external/few-label tracks. That is genuine new pilot work; it is not by itself proof of a new research question.
''')
report('engineering_artifact.md',f'''# Executed local Data Quality Evaluation Service

Python package: `dq_service`, entrypoint **dqeval** (or `python -m dq_service`). The artifact is a local CLI/research service, not an HTTP deployment or frontend.

Supported path: register a CSV+schema contract → pin its source hash → load separate historical values → run A/B controls → run a compatible detector adapter → write coordinate findings and machine-readable report → return a bounded recommendation. A changed registered source hash fails instead of silently refreshing provenance. Declared outcome/reference feature names are rejected. Wrong feature alignment, invalid numeric strings and incompatible target units have negative tests.

Selectable scan adapters: contextual_extra_trees, original dBoost text, original LUCARIO history inference and original CDC. Separate environments preserve incompatible Python/library requirements. A native failure leaves control results available and records BLOCKED_TECHNICAL rather than fabricating zero model alerts. Native source/rights and information caveats still apply.

The generic `experiment` command supports registered-source missing/type/code/scale/substitution interventions using official ECAR/EAR/ENAR placement, separate history, A/B and contextual ExtraTrees, untouched counterfactuals, review budgets and machine-readable outputs. It writes a dirty copy and local value log without changing the registered file. The executed synthetic type demo creates {registered['realized_changes']} new violations among {registered['eligible_count']} eligible rows; ExtraTrees explicitly abstains on unparseable numeric targets. Scale/substitution are labelled alterations. This service demonstration is separate from the 630 primary scenarios.

Actually executed demo: 200 explicitly synthetic transactions, 40 accounts and a paired-entry ledger. Eight mutations exercise missing parents, duplicate IDs, invalid status, missing delivery, imbalance, source/ledger mismatch, requiredness and numeric validity. Untouched fixture passes its stipulated invariants. Registration and scans executed with both ExtraTrees and original dBoost. The two known lexical/domain violations are found by basic controls; additional statistical findings remain suspicion. The unlabeled scan returns INSUFFICIENT_EVIDENCE, not adoption based on alert volume.

```
bash scripts/setup_thesis_pilot.sh
PYTHONPATH=src data/envs/pilot/bin/python scripts/engineering_fixture.py
data/envs/pilot/bin/dqeval --help
# Generic new-source contract registration and scan:
data/envs/pilot/bin/dqeval register --id my_source --csv /path/new.csv --contract /path/contract.json
data/envs/pilot/bin/dqeval scan --id my_source --history /path/history.csv --output /path/findings --detector contextual_extra_trees
# Generic intervention evaluation on a copy of that registered source:
data/envs/pilot/bin/dqeval experiment --id my_source --history /path/history.csv --target amount --family type --rate .05 --output /path/experiment
# Full scientific reproduction (checkpointed, labels/scopes explicit):
bash scripts/reproduce_thesis_pilot.sh
```

Recommended source layout is the existing checkout; every cloud task is already isolated, so do not create a Git worktree. Source caches, original data, local injection-value logs and fitted weights remain ignored. Package locks and source revisions are committed; `setup_thesis_pilot.sh` was executed successfully against the prepared environment. Fresh-instance cloud restoration has not been verified.

Local LLM: {llm['model']['model']} revision {llm['model']['revision']}, Q8_0 SHA-256 {llm['model']['sha256']}, local llama.cpp completion, temperature 0, seed 42, 2 CPU threads, {llm['seconds']:.2f} seconds. Public schema only, no private records, labels or paid APIs. {llm_outcome} This is neither Qwen3-8B evaluation nor original ZeroED reproduction. Optional build/acquisition/generation scripts and logs remain separate from the core study.

`dq_service.recommend` supports ADOPT / DO_NOT_ADOPT / INSUFFICIENT_EVIDENCE only under explicit scope, semantic-reference and review-cost prerequisites. Current pilot outputs support bounded DO_NOT_ADOPT for already covered stipulated schema families and INSUFFICIENT_EVIDENCE for broad operational adoption. Test fixtures exercising an ADOPT branch are policy tests, not empirical adoption evidence.
''')
report('independent_audit.md',f'''# Independent computational and skeptical scientific audit

Primary independent script imports neither the production injector nor scoring/scheduling functions. It reopens source archives, verifies hashes/outcome exclusion/duplicate-group partitions, reconstructs ECAR/EAR/ENAR locations without tab_err, checks every original/new logged value and operation, re-counts truth coordinates, all unconstrained/incremental/budget/new-trigger metrics and displacements.

Result: **{sum(verification['checks'].values()):,} primary assertions passed over 630 scenarios and 52,740 metric rows**. Supplemental independent arithmetic: **{supp['total_assertions']:,} assertions**, including published references, the metered label regime, identical transformations across mechanisms, all-feature/type probes, 45 row scenarios, hard-priority capacity and actual CLI executions. Detailed categories are in the JSON verification files. This is an independently coded implementation, not a second human annotator or external academic examiner.

{test_count} software tests pass in the full pilot environment. The original audit-only environment passes its 29 tests and explicitly skips the optional pilot module because numerical dependencies are separate. Its skip is not used to claim new experiment readiness. No zero-test success or missing model is counted as passing detection.

Supported: acquired byte identities, controlled operations under stipulated contracts, exact native example parity, documented implementation executions, source-specific reference-relative increments and measured review burden. Unsupported: verified natural correctness of every benchmark cell, bank production efficacy, independent customer/source confidence, globally mature business controls, novelty confirmation or original ZeroED/complete Auto-Test scores.

Challenges retained: B is richer but research-defined; hard-rule prioritisation changes operational interpretation; duplicate-feature groups are not known independent customers; native CDC dtype/calibration and boundary behaviour can inflate alerts; LUCARIO coverage assumptions are challenged by 10% contamination; binary flag order is not optimal ranking; history source values are not certified clean. Publisher-reference performance and alteration recovery cannot be combined into one semantic F1.

No unresolved unexpected primary model execution failure remains among applicable combinations. The 405 method/scenario exclusions are explicit input-domain limitations (270 numeric dBoost; 135 CDC lexical numeric), not dropped records or zero scores. Remaining scientific limitations restrict the claim and final-study design rather than stopping unaffected tracks.
''')
report('final_recommendation.md',f'''# Final recommendation

**CONDITIONAL GO for a focused empirical MSc AI thesis.** The pilot now executes; the earlier audit-only broad stop no longer blocks controlled interventions. This is not a completed final thesis, a confirmed novel contribution or a justified bank deployment.

{primary_claim}

The supported thesis direction is: **incremental detector value conditional on independently specified baseline controls, valid error/alteration targets, information access and a fixed human-review capacity**. Keep mechanism sensitivity as a measured secondary dimension. Do not return to detector-selection-diversity as the main hypothesis or claim that combining AI with rules is new.

Actual evidence: 3 complete acquired sources, 630 final primary cell scenarios (210 per mechanism), 45 separate Bank row-contract cases, five primary detector configurations (two dBoost encodings are one family), two publisher-reference tables, original Raha's metered-label regime, 36 feature/type probes, 8 linked-table fixture cases and a real local rule-generation run. Source-specific rule completion eliminates increments for the stipulated E1/E2/E3 targets. Some learned alteration recovery remains, often with large review burden or capacity losses. None of this proves detection of all natural financial errors.

Exact next steps:

1. Agree with supervisors on the contribution relative to Auto-Test/REIN/complementarity literature and the distinction between operational contract errors and plausible alterations. Long's operational motivation is represented, but no personal approval is inferred.
2. Before confirmation, freeze detector type/input/calibration conventions and review priority using documentation and development data. Native CDC and its declared-type diagnostic must remain distinct; resolve/discuss discrete-boundary behaviour rather than selecting whichever test outcome looks best.
3. Retain credible hard constraints plus training-only statistical controls and a hard-contract-priority review policy. Expand legitimate source-specific cross-field rules only where their semantics and output unit are justified; use linked fixtures for referential/reconciliation engineering.
4. Obtain genuinely independent source/batch/entity metadata or new sources for confirmation; current exact-duplicate groups and five seeds do not create source-level replications. Preserve the reserved groups and do not call prior inspected public data pristine.
5. Run a prespecified compatible detector subset on the same target universe, retain negative/unknown outcomes, and measure reviewer usefulness/cost if an operational adoption claim is desired. Broader natural-error claims require independently defensible references; Hospital/Beers only provide qualified external agreement here.

Recommend **DO_NOT_ADOPT solely for additional coverage of already-complete stipulated schema families**; **INSUFFICIENT_EVIDENCE for operational adoption of the learned methods overall**. The source-registration and evaluation CLI actually runs. The engineering artifact is useful alongside the science; its existence and passing tests do not establish novelty or semantic correctness.
''')
# Auditable registries and an acceptance matrix distinguish execution from full-paper fidelity.
rule_rows=[]
for name in pops:
 contract=read(f'results/thesis_pilot/{name}_contracts.json')['contract']
 targets=pops[name]['evaluated_targets'];parts,_=load(name);history=parts['history'][targets]
 assert list(history.index)==pops[name]['parts']['history']
 fitted=Controls(contract,targets,[c for c in SPECS[name]['categorical'] if c in targets]).fit(history)
 for column in pops[name]['evaluated_targets']:
  spec=contract[column]
  def rule(control,provenance,parameters,evidence,hard):
   rule_rows.append({'dataset':name,'column':column,'control':control,'baseline':'A_and_B' if hard else 'B','provenance':provenance,'parameters':parameters,'evidence':evidence,'hard_validity':hard})
  rule('requiredness','EXPLICIT_STIPULATED_CONTRACT',{'required':True},'Frozen operational feed contract; publisher-wide completeness is not asserted.',True)
  if spec['type']=='numeric':
   rule('numeric_lexical_finite','EXPLICIT_STIPULATED_CONTRACT',{'type':'finite numeric'},spec['evidence'],True)
   if 'bounds' in spec:rule('numeric_bounds',spec['bounds_provenance'],{'bounds':spec['bounds']},spec['bounds_evidence'],True)
   rule('history_quantiles_and_IQR','TRAINING_ONLY_STATISTICAL_CONTROL',{'quantiles':[.005,.995],'IQR_multiplier':3,'fitted_limits':fitted.stats[column]},'Fit only on the approved unique full-feature history; values are statistical suspicion.',False)
   rule('conditional_Ridge_residual','TRAINING_ONLY_STATISTICAL_CONTROL',{'alpha':10,'fit_fraction':.75,'calibration_fraction':.25,'residual_quantile':.995,'quantile_method':'higher','fitted_residual_cutoff':fitted.models[column][3],'predictor_columns':fitted.models[column][0]},'Other permitted primary fields predict target; no held-out intervention/reference labels.',False)
  else:
   rule('categorical_domain',spec['provenance'],{'domain':spec['domain']},spec['evidence'],True)
   rule('history_category_frequency','TRAINING_ONLY_STATISTICAL_CONTROL',{'minimum_share':.005,'fitted_shares':fitted.stats[column]['shares']},'Fit only on the approved unique full-feature history; uncommon does not mean semantically invalid.',False)
(R/'manifests/thesis_pilot/rule_provenance.json').write_text(json.dumps({'scope':'Applied primary four-field controls; separate row/linked-fixture contracts in their own protocols. Fitted values deterministically reconstructed from the identical frozen source/history and implementation, with no evaluation values or labels.','controls':rule_rows,'primary_not_applicable':['foreign-key consistency: no parent table','ledger reconciliation: no legitimate linked balance','key uniqueness: no documented evaluated entity key']},indent=2)+'\n')
registry={'primary_configurations':[{'name':m,'scenarios_scored':n,'output':'binary cell flags','ranking_or_pr_auc':'NOT_CLAIMED'} for m,n in coverage.items() if m not in ['A','B']],'regimes':{'primary':'approved untouched-source history, no error labels; source not certified clean','external':'transductive publisher-reference agreement','raha':'20 metered labelled rows, excluded from evaluation','llm':'public schema only; no automatic promotion'},'source_types_diagnostic':'separate adaptation, 18 scenarios; full input features, same four targets','basic_coverage_operational_scenarios':360,'tracks':{'controlled_interventions':'EXECUTED_CONDITIONAL','published_reference_errors':'EXECUTED_CONDITIONAL','recent_detector_reproduction':'EXECUTED_CONDITIONAL','local_llm_rule_generation':'EXECUTED_CONDITIONAL','engineering_artifact':'EXECUTED_VALID'},'unavailable':{'AutoTest':'NOT_EXECUTED full inference; bounded setup attempts','ZeroED':'NOT_EXECUTED full pipeline; source/paper reviewed'},'global_adoption':'INSUFFICIENT_EVIDENCE'}
(R/'manifests/thesis_pilot/method_registry.json').write_text(json.dumps(registry,indent=2)+'\n')
acceptance={'datasets':3,'primary_cell_scenarios':630,'bank_row_scenarios':len(rows),'scope_probes':len(rich),'source_type_probes':len(typed),'metrics':manifest['metric_rows'],'tests':f'{test_count} PASSED in pilot environment; 29 PASSED/1 module SKIPPED in original audit environment','independent_primary_checks':sum(verification['checks'].values()),'independent_supplemental_checks':supp['total_assertions'],'full_lucario_original_components':'EXECUTED; author-example exact parity; history-fit regime explicit','faithful_published_learned_execution':'CDC original pipeline with restricted supported RF/XT portfolio, assumptions conditional; Raha original KB-disabled few-label regime separate','external_status':'two publisher-reference sources, not independent semantic gold standard','engineering_cli':'EXECUTED_VALID','novelty':'NOT_ESTABLISHED; supervisor/literature gate for confirmation','research_feasibility':'CONDITIONAL_GO','scope_limitations':primary_claim}
(O/'acceptance.json').write_text(json.dumps(acceptance,indent=2)+'\n')
print(json.dumps(acceptance,indent=2))
