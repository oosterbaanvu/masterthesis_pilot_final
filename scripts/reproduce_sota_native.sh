#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sota_repo_root="$PWD"
export PYTHONPATH=src OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONHASHSEED=13 TF_CPP_MIN_LOG_LEVEL=2
export HF_HOME="$PWD/data/huggingface" TORCH_HOME="$PWD/data/torch_cache" TRANSFORMERS_CACHE="$PWD/data/huggingface/transformers" NLTK_DATA="$PWD/data/nltk_data" MPLCONFIGDIR="$PWD/data/matplotlib"
data/envs/sota/bin/python - <<'PY'
import json
from thesis_pilot.data import ROOT
from sota_followup.benchmarks import load_benchmark
for name in ['rt','st']:
 rows,_=load_benchmark(name);(ROOT/f'data/sota_followup/autotest_input_{name}.json').write_text(json.dumps([{k:r[k] for k in ['position','header','values']} for r in rows]))
PY
data/envs/autotest37/bin/python scripts/sota_repair_autotest_cache.py
case "${1:---cache-check}" in
  --cache-check) ;;
  --benchmarks)
    data/envs/autotest37/bin/python scripts/sota_autotest_full.py --benchmark rt --corpus rt_train
    data/envs/autotest37/bin/python scripts/sota_autotest_full.py --benchmark st --corpus st_train
    data/envs/autotest37/bin/python scripts/sota_autotest_raw_audit.py
    ;;
  --authors-demo)
    cd data/sota_followup/autotest37_source
    "$sota_repo_root/data/envs/autotest37/bin/python" online_detect.py unit_test/example.csv results/SDC/rt_train_selected_sdc.csv
    ;;
  *) echo 'Use --cache-check, --benchmarks or --authors-demo' >&2; exit 2 ;;
esac
