#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
export MPLCONFIGDIR="$PWD/data/matplotlib"
mkdir -p "$MPLCONFIGDIR" evidence/thesis_pilot
# Run setup_thesis_pilot.sh first if environments/sources are missing.
data/envs/pilot/bin/python scripts/acquire_pilot_data.py
data/envs/pilot/bin/python -m pytest tests -q > evidence/thesis_pilot/all_tests.log 2>&1
data/envs/lucario/bin/python scripts/reproduce_lucario_authors.py > evidence/thesis_pilot/lucario_authors_reproduction.log 2>&1
data/envs/pilot/bin/python -m thesis_pilot.run > evidence/thesis_pilot/full_grid.log 2>&1
data/envs/pilot/bin/python scripts/verify_pilot_independently.py > evidence/thesis_pilot/independent_verification.log 2>&1
data/envs/pilot/bin/python scripts/analyze_pilot.py > evidence/thesis_pilot/analysis.log 2>&1
data/envs/pilot/bin/python scripts/external_pilot.py > evidence/thesis_pilot/external_execution.log 2>&1
data/envs/raha/bin/python scripts/reproduce_raha.py > evidence/thesis_pilot/raha_execution.log 2>&1
data/envs/pilot/bin/python scripts/engineering_fixture.py > evidence/thesis_pilot/engineering_execution.log 2>&1
data/envs/pilot/bin/python scripts/full_feature_probe.py > evidence/thesis_pilot/full_feature_probe.log 2>&1
data/envs/pilot/bin/python scripts/cdc_type_diagnostic.py > evidence/thesis_pilot/cdc_type_diagnostic.log 2>&1
data/envs/pilot/bin/python scripts/bank_crossfield_rows.py > evidence/thesis_pilot/bank_crossfield_rows.log 2>&1
data/envs/pilot/bin/python scripts/review_priority_sensitivity.py > evidence/thesis_pilot/review_priority_sensitivity.log 2>&1
data/envs/pilot/bin/python scripts/profile_pilot_methods.py > evidence/thesis_pilot/resource_profile.log 2>&1
data/envs/pilot/bin/python scripts/retest_dboost_period.py > evidence/thesis_pilot/dboost_period_retest.log 2>&1
data/envs/pilot/bin/python -m dq_service scan --id synthetic_finance_demo --history data/engineering_fixture/transactions.csv --output results/thesis_pilot/service_native_demo --detector dboost_text_original > evidence/thesis_pilot/service_native_demo.log 2>&1
data/envs/pilot/bin/python -m dq_service experiment --id synthetic_finance_demo --history data/engineering_fixture/transactions.csv --target amount_cents --family type --rate .05 --seed 42 --output data/registered_service_intervention > evidence/thesis_pilot/registered_intervention_demo.log 2>&1
cp data/registered_service_intervention/report.json results/thesis_pilot/service_registered_intervention.json
data/envs/pilot/bin/python scripts/sanitize_model_metadata.py
data/envs/pilot/bin/python scripts/verify_supplements.py > evidence/thesis_pilot/supplement_verification.log 2>&1
data/envs/pilot/bin/python scripts/build_thesis_pilot_reports.py
data/envs/pilot/bin/python scripts/verify_reported_numbers.py > evidence/thesis_pilot/report_verification.log 2>&1
printf 'Exploratory pilot and independent checks complete; read the scientific limitations.\n'
