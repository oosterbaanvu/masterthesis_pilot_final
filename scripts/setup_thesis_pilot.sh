#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_CACHE_DIR="$PWD/data/uv-cache"
export UV_PYTHON_INSTALL_DIR="$PWD/data/uv-python"
python scripts/setup_pilot_sources.py
uv python install --no-bin 3.9
uv venv --allow-existing --python 3.12 data/envs/pilot
uv venv --allow-existing --python "$PWD/data/uv-python/cpython-3.9-linux-x86_64-gnu/bin/python3.9" data/envs/cdc
uv venv --allow-existing --python "$PWD/data/uv-python/cpython-3.9-linux-x86_64-gnu/bin/python3.9" data/envs/lucario
uv venv --allow-existing --python "$PWD/data/uv-python/cpython-3.9-linux-x86_64-gnu/bin/python3.9" data/envs/raha
for target in pilot cdc lucario raha; do
  uv pip install --python "data/envs/$target/bin/python" --no-deps -r "envs/thesis_pilot/$target.lock.txt"
done
uv pip install --python data/envs/pilot/bin/python --no-deps -e .
PYTHONPATH=src data/envs/pilot/bin/python scripts/acquire_pilot_data.py
