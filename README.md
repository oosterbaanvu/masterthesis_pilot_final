# SOTA and nontrivial error extension — executed exploratory thesis pilot

The new follow-up is on **research/sota-dataset-extension**. Start with the [thesis decision](reports/sota_followup/11_thesis_decision.md), [review-budget results](reports/sota_followup/07_incremental_value_and_shared_review_budget.md) and [execution/reproduction manifest](reports/sota_followup/00_execution_manifest.md). The twelve follow-up reports are in [reports/sota_followup](reports/sota_followup/).

| New executed work | Scope |
| --- | --- |
| Source-relative interventions | 360 logical numeric/category cases × two feature views = 720 cases; another 135 lexical occurrence cases |
| Original Auto-Test | Fresh authors online demo; full released RT/ST inference with 505/509 SDCs, 35/23 native outliers; benchmark neural caches reused with audited input repair |
| Original RIOLU | 2997 author-example flags match; publisher/P5 experiments; default 385-value applicability separated from small-sample adaptation |
| Stronger controls | R / R+S / R+S+M separated; cheap categorical classifier sensitivity; shared review capacity and displacement |
| Decision | **CONDITIONAL GO** for a bounded empirical thesis; novelty and bank production benefit not established |

At 25 distinct-value reviews, full Auto-Test adds 5 RT / 4 ST publisher-positive hits beyond generic profiles under equal-share scheduling. A stronger same-corpus pattern-first comparator reduces that to **3 RT / 1 ST**. Control-first scheduling yields no increment at that capacity. Numeric CDC's larger unconstrained unions often add hundreds of alerts, with little or negative reviewed net value; cheap categorical controls remove some apparent gains. Injected changes establish source alteration, not natural semantic errors. No global detector leaderboard across incompatible units/information regimes.

```bash
bash scripts/setup_sota_followup.sh             # pinned environments and checksum-verified public artifacts
bash scripts/verify_sota_followup.sh            # independent replay of saved predictions + software tests
PYTHONPATH=src data/envs/sota/bin/python scripts/sota_service_demo.py
bash scripts/reproduce_sota_native.sh --cache-check
# For fresh native execution in a separate output checkout:
bash scripts/reproduce_sota_native.sh --authors-demo
bash scripts/reproduce_sota_native.sh --benchmarks
```

The CLI adds `pattern-scan` (original RIOLU, small-sample RIOLU, native LUCARIO, AutoTest-pattern-only) and `sota-benchmark` (full original pretrained Auto-Test). Scanning is separate from oracle evaluation; incompatible inputs return NOT_APPLICABLE/null. Model/source/data rights and deviations are in [method registry](manifests/sota_followup/method_registry.json) and [compatibility matrix](manifests/sota_followup/compatibility_matrix.json). No raw datasets, weights or third-party source copies are committed. No paid API is needed. Original ZeroED/SAGED remain unexecuted; the separate local ZeroED structural adaptation actually runs its MLP but contributes zero hits beyond its synthetic hard controls. Full primary-paper novelty review is incomplete for LUCARIO and tab_err.

The complete preceding pilot remains preserved below and under `reports/thesis_pilot` / `results/thesis_pilot`. Its statements describe that earlier stage; the follow-up above supersedes earlier full-Auto-Test feasibility status. Current-instance setup was replayed; a fresh cloud snapshot restoration has not been independently verified.

---

# Incremental data-quality detection — executed MSc AI research pilot

**Current status: substantial exploratory pilot executed; CONDITIONAL GO for a focused thesis, no production adoption claim.** This research branch extends the preserved original dataset audit with actual models, interventions, review budgets, external-reference checks and a working local CLI.

Start with the [executive summary](reports/thesis_pilot/executive_summary.md), [actual results](reports/thesis_pilot/experimental_results.md), [independent audit](reports/thesis_pilot/independent_audit.md) and [final recommendation](reports/thesis_pilot/final_recommendation.md).

## What actually ran

| Track | Executed scope |
| --- | --- |
| Complete original sources | UCI Credit 30,000 × 25, Bank Marketing 41,188 × 21, White Wine 4,898 × 12 |
| Primary cell pilot | **630 scenarios**, ECAR/EAR/ENAR 210 each; rates 1/5/10%, five fixed seeds; **52,740 metric rows** |
| Primary methods | Original dBoost text/numeric (one family), complete original LUCARIO inference with explicit history fitting, original CDC in its Python 3.9 environment, separately named contextual ExtraTrees adapter |
| Cross-field validation | **45 Bank row-level scenarios**, separately stipulated previous-campaign relation; no invented cell blame |
| Information/type diagnostics | **18** all-feature probes and **18** source-type CDC adaptations; not pooled into primary outcomes |
| External references | Hospital/Beers with LUCARIO+dBoost; separate original Raha KB-disabled learning pipeline with **20 labelled rows**, excluded from its evaluation |
| Engineering | Registration, contracts, source hashes, A/B controls, compatible adapters, findings, recommendations and **8 synthetic linked-table mutations** |
| Local model | Verified Qwen3-0.6B Q8_0 through local llama.cpp; initial ambiguous output preserved; one clarified retry yields two baseline duplicates and two schema-type repetitions without incremental evaluation; no private records or paid APIs |

The primary views score four predeclared fields per source, using 800 evaluation rows and at most 2,400 historical rows. Full sources were acquired, but this is not exhaustive all-field evaluation. Duplicate feature vectors are grouped; this does not establish customer or source-population independence. The source-history values are not certified perfectly clean.

Basic and extended controls detect all stipulated missing/type/code violations. Some detectors recover additional plausible/scale **changes**, sometimes with very large extra alert burden. Alteration recovery is not independently verified semantic-error detection. Unknown untouched-cell alerts are not automatically false positives. Shared-capacity losses, source-specific results, inapplicabilities and negative findings remain visible. Novelty is not yet established.

## Reproduce the non-LLM research and service

Requires Linux, Git, `uv`, Python 3.12 and access to the pinned official package/data sources. Work in the existing checkout: each cloud task is already isolated; do not create a Git worktree.

```bash
cd /workspace/masterthesis_pilot_final
bash scripts/setup_thesis_pilot.sh
bash scripts/reproduce_thesis_pilot.sh

# Independent arithmetic checks (no re-fitting):
data/envs/pilot/bin/python scripts/verify_pilot_independently.py
data/envs/pilot/bin/python scripts/verify_supplements.py

# Actual reusable source-registration and scan demonstration:
PYTHONPATH=src data/envs/pilot/bin/python scripts/engineering_fixture.py
data/envs/pilot/bin/dqeval --help
# Registered-source interventions on a copy, with original-source hash preservation:
data/envs/pilot/bin/dqeval experiment --id synthetic_finance_demo \
  --history data/engineering_fixture/transactions.csv --target amount_cents \
  --family type --rate .05 --seed 42 --output data/registered_service_intervention
```

Exact environment locks live in `envs/thesis_pilot/`; original source revisions/rights in `configs/thesis_pilot/sources.json`; raw-source hashes in `manifests/thesis_pilot/datasets.json`. The setup script preserves existing source checkouts and fails on a conflicting revision rather than resetting user changes. Native learned constraints are retained locally and sanitized to summaries before commit.

`results/thesis_pilot/scenarios/` stores each completed case and its prediction/injection-log hashes; `predictions/` contains boolean outputs and truth masks. Full original/new injection values are local-only under ignored `data/pilot_runs/`, and reconstruct exactly from source/version/seed. Re-running the same code/protocol reuses completed scenario checkpoints. A changed fingerprint requires a versioned rerun, not overwriting evidence. The superseded v1.1/v1.2 grids and smoke runs remain under `attempts/`. Final v1.3 also removes known full-feature duplicates from history before internal calibration; it keeps the same evaluation rows and interventions and explicitly changes history frequency weights.

The main pipeline repeats the original-example parity test, core verification/analysis, external/few-label comparisons, full-feature/type/row diagnostics and service demo. The optional local LLM record is retained as a separately executed experiment; it is not regenerated by the default non-LLM command. No complete Auto-Test or ZeroED performance is claimed.

## Optional local rule-generation reproduction

The model weights and runtime build outputs are ignored. Authoritative LFS checksums and the pinned model/runtime revisions are recorded. On this host the backend built as `llama-completion`; the initially attempted `llama-cli` target was unavailable in that configuration.

```bash
python scripts/setup_pilot_sources.py --all
PYTHONPATH=src data/envs/pilot/bin/python scripts/acquire_local_model.py
PATH="$PWD/data/envs/pilot/bin:$PATH" data/envs/pilot/bin/cmake \
  -S data/sources/llama.cpp -B data/llama_build -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_SERVER=OFF \
  -DGGML_OPENMP=OFF -DGGML_NATIVE=OFF
PATH="$PWD/data/envs/pilot/bin:$PATH" data/envs/pilot/bin/cmake \
  --build data/llama_build --target llama-completion -j 2
data/envs/pilot/bin/python scripts/local_rule_generation.py
```

Only public schema information reaches this local model. Output is parsed and checked against independently specified contracts; parsing alone does not validate a rule. No generated rule is automatically promoted, and this is not an original ZeroED reproduction.

## Evidence and reports

- [Research design](reports/thesis_pilot/research_design.md), [dataset qualification](reports/thesis_pilot/dataset_qualification.md), [rule provenance](reports/thesis_pilot/rule_baselines.md)
- [Intervention validation](reports/thesis_pilot/injection_validation.md), [detector reproduction](reports/thesis_pilot/detector_reproduction.md), [external validation](reports/thesis_pilot/external_validation.md)
- [Incremental-value analysis](reports/thesis_pilot/incremental_value_analysis.md), [issues and retests](reports/thesis_pilot/domain_issues_and_repairs.md), [literature/novelty](reports/thesis_pilot/literature_and_novelty.md)
- [Engineering artifact](reports/thesis_pilot/engineering_artifact.md), [final recommendation](reports/thesis_pilot/final_recommendation.md), [independent audit](reports/thesis_pilot/independent_audit.md)

The original audit reports `reports/01_*.md` through `10_*.md`, original manifests and acquisition code are preserved. Their audit-only NO-GO is historical and does not describe this new executed intervention track. The [previous README](reports/thesis_pilot/previous_audit_README.md) is preserved for provenance. The original lightweight workflow remains available via `scripts/setup.sh` / `scripts/reproduce.sh`; it does not replace the new scientific environments or checks.

Raw datasets, copyrighted publications, third-party checkouts, checkpoints and trained weights remain ignored under `data/`. UCI data attribution and all source/rights limitations remain in the manifests/reports. No private bank data is used. No fresh cloud-task restoration, production deployment, independent human annotation or supervisor approval is claimed.
