#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=0
# Reuses committed predictions; does not call a model or overwrite primary outputs.
data/envs/sota/bin/python scripts/sota_restore_logs.py
data/envs/sota/bin/python scripts/sota_verify_ingest.py
data/envs/sota/bin/python scripts/sota_verify_supplement.py
data/envs/sota/bin/python -m pytest -q
