#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_CACHE_DIR="$PWD/data/uv-cache"
export UV_PYTHON_INSTALL_DIR="$PWD/data/uv-python"
export PIP_CACHE_DIR="$PWD/data/pip-cache"
export CONDA_PKGS_DIRS="$PWD/data/envs/autotest37/pkgs"
export CONDA_ENVS_PATH="$PWD/data/conda-envs"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
mkdir -p data/envs data/conda-envs data/sota_followup
python scripts/setup_pilot_sources.py --all
uv python install --no-bin 3.9
uv venv --allow-existing --python 3.12 data/envs/sota
for target in cdc lucario; do
  uv venv --allow-existing --python "$PWD/data/uv-python/cpython-3.9-linux-x86_64-gnu/bin/python3.9" "data/envs/$target"
done
for target in sota cdc lucario; do
  uv pip install --python "data/envs/$target/bin/python" --no-deps -r "envs/sota_followup/$target.lock.txt"
done
# Original text dBoost worker uses the preceding pilot runtime.
if [ ! -x data/envs/pilot/bin/python ]; then
  uv venv --python 3.12 data/envs/pilot
  uv pip install --python data/envs/pilot/bin/python --no-deps -r envs/thesis_pilot/pilot.lock.txt
fi
uv pip install --python data/envs/sota/bin/python --no-deps -e .
PYTHONPATH=src data/envs/sota/bin/python scripts/acquire_pilot_data.py
PYTHONPATH=src data/envs/sota/bin/python scripts/sota_acquire.py --models --python37
if [ ! -x data/envs/autotest37/bin/python ]; then
  if ! bash data/sota_followup/Miniconda3-py37_23.1.0-1-Linux-x86_64.sh -b -p "$PWD/data/envs/autotest37"; then
    # The immutable-home image can interrupt registry initialization after extracting
    # verified embedded packages. Resume only that installer's exact offline plan.
    test -x data/envs/autotest37/conda.exe
    test -f data/envs/autotest37/pkgs/env.txt
    data/envs/autotest37/conda.exe install --offline --file "$PWD/data/envs/autotest37/pkgs/env.txt" -yp "$PWD/data/envs/autotest37"
  fi
fi
# The authors' TF1.15.5 and NumPy>=1.21 requirements conflict in metadata.
# Exact observed successful versions are intentional, not dependency-solver success.
data/envs/autotest37/bin/python -m pip install --no-deps --extra-index-url https://download.pytorch.org/whl/cpu -r envs/sota_followup/autotest37.lock.txt
python scripts/sota_prepare_autotest.py
bash scripts/reproduce_sota_native.sh --cache-check
PYTHONPATH=src data/envs/sota/bin/python -m pytest -q
