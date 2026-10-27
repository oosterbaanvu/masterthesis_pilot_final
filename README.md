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
