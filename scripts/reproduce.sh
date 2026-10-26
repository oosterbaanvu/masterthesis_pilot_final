#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/src"
.venv/bin/python -m thesis_audit.acquire --log evidence/acquisition.json
.venv/bin/python -m thesis_audit.audit > evidence/audit_stdout.log 2> evidence/audit_stderr.log
.venv/bin/python scripts/audit_supplementary.py > evidence/supplementary_stdout.log
.venv/bin/python scripts/verify_independently.py > evidence/independent_stdout.log
.venv/bin/python -m pytest -q > evidence/pytest.log 2>&1
.venv/bin/python scripts/build_reports.py
printf 'Audit reproduced. Detector benchmark pilot remains scientifically gated.\n'
