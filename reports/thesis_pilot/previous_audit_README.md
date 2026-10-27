# MSc AI thesis: dataset qualification before detector experiments

**Current decision: NO-GO for immediate confirmatory multi-table execution.** A narrower published column-value study is conditional. There is no new AI-performance result. [Decision and next experiment](reports/08_final_go_no_go.md) · [independent computational/scientific audit](reports/09_independent_scientific_audit.md).

The original assignment and additional instructions are preserved privately in ignored attachments outside this checkout. This repository contains new research code, evidence, ten reports, pinned acquisition manifests, qualification/compatibility matrices and a provisional experiment configuration. Historical repositories were inspected read-only, not imported as a framework.

## What actually works

- 29 source files/archives pinned by full checksum, URL, byte length and revision; clean-directory acquisition verified.
- Nine released dirty/reference pairs completely audited, including the illustrative Toy fixture (not a research dataset).
- Conservative Auto-Test subsets: RT 1,194 columns / 90,934 distinct values / 41 publisher positives; ST 1,193 / 71,719 / 45. These are not occurrence-weighted cells or semantic errors independently adjudicated here.
- UCI Credit 30,000 × 25 and Bank 41,188 × 21 acquired; **outcomes are not DQ labels**.
- 29 deterministic tests, including deliberate reference-leakage negatives, unit compatibility and baseline numeric guards; independent raw-data recounts and original dBoost fixture execution.
- No semantic human annotation, detector leaderboard, completed extended baseline or certified novelty.

## Reproduce

Python 3.11+ (tested Python 3.12.14), Git and network access to pinned official sources are required. Work in this existing checkout; each cloud task is already isolated, so do not create a Git worktree.

```bash
cd /workspace/masterthesis_pilot_final
bash scripts/setup.sh
bash scripts/reproduce.sh

# Clean-directory second acquisition; original raw files are untouched.
PYTHONPATH=src .venv/bin/python -m thesis_audit.acquire \
  --root data/clean_acquisition --log evidence/clean_acquisition.json

# Optional exact pinned paper acquisition (PDF reading requires pdftotext).
PYTHONPATH=src .venv/bin/python -m thesis_audit.acquire \
  --manifest manifests/literature.json --log evidence/literature_verification.json

# Actual upstream engineering smoke test, not a detector benchmark.
.venv/bin/python scripts/fetch_sources.py --only cpitclaudel/dBoost
.venv/bin/python scripts/check_dboost.py

# Optional read-only archaeology of all ten pinned source checkouts.
.venv/bin/python scripts/fetch_sources.py
```

No credential or paid inference API is required. Raw data, originals, derived labels, stratified samples, blind-review packets, publications and reconstructed source checkouts are ignored under `data/`. Reacquisition fails on changed bytes rather than silently refreshing hashes. Local auditing does not establish redistribution permission; do not add data to Git. Archive/member checksums, numeric string handling, source-key definitions and licence limitations are in reports 01–03 and manifests.

`data/derived/*_labels.csv` records every difference. `*_sample.json` records original/reference values, row/column coordinates and reasons; `*_blind_review.json` removes our interpretation for future independent review. Since these contain source records, regenerate them locally rather than committing them. Empty arrays, absent labels and malformed expressions are not interchangeable.

`configs/protocol_v0.1.json` is an audit-stage provisional freeze with `execution_allowed=false`. Any later primary pilot must first qualify its datasets, control contracts, rights and method information access. These public sources have already been inspected; none is a pristine confirmatory holdout. No web app or services need starting.

## Reports

1. [Dataset inventory](reports/01_dataset_inventory.md)
2. [Ground-truth audit](reports/02_ground_truth_audit.md)
3. [Method compatibility](reports/03_domain_and_method_compatibility.md)
4. [Baseline design](reports/04_baseline_design.md)
5. [Literature and novelty](reports/05_literature_and_novelty.md)
6. [Research protocol](reports/06_research_protocol.md)
7. [Pilot execution status](reports/07_pilot_results.md)
8. [Go/no-go decision](reports/08_final_go_no_go.md)
9. [Independent audit](reports/09_independent_scientific_audit.md)
10. [Repair/retest register](reports/10_issue_resolution_log.md)

Evidence is computational, not a replacement for independent semantic annotation or supervisor approval of the research contribution. A useful negative detector outcome remains acceptable; no outcome has been manufactured to justify continuation.
