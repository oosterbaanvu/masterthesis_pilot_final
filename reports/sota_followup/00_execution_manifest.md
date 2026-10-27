# Executed follow-up: provenance and reproduction

This is an **executed exploratory extension**, on `research/sota-dataset-extension`, based on `46b9f3171aa9200b5b1cc97bb97ed70b2b38082b` (the full-scale research branch, not old main). The working tree was clean before branching. HEAD while preparing this report was `8ffdb072235a0544735c16ed80cc2021d6087657`; the inference protocol was checkpointed in `8ffdb07`. The final delivery SHA is the commit containing this report or its branch tip (`git rev-parse HEAD`), also supplied with the GitHub delivery. A file cannot contain its own final Git object hash.

Hardware: Linux x86_64, 4CPU quota/5CPU affinity, 32GiB memory limit, **no GPU**. Native thread/process counts were bounded; Auto-Test uses two workers. No paid model calls/cloud purchases. No private bank data or new credentials. Original files under `reports/thesis_pilot`, `results/thesis_pilot`, `manifests/thesis_pilot`, `src/thesis_pilot` remain unchanged.

| Track | Actual new work |
| --- | --- |
| Numeric/contextual source alterations | 360 logical cases ×2 views =720; 120,960 metric rows |
| Lexical source alterations | 135 cases, 800 actual occurrences/source |
| Original Auto-Test | Fresh authors online demo7×5; full RT 1194/ST 1193 column inference; 505/509 released SDCs |
| RIOLU | Original authors example2997 compared flags, zero adapter disagreement; matched publisher and P5 runs |
| Historical baseline taxonomy | Cached630 cases reused; zero historical advanced refits |
| Diagnostics | Six canonical CDC fits/16 cases; four categorical comparator fits/720-case replay; local MLP actual execution |

Evidence is in `evidence/sota_followup/`, source/model/data SHA records in `manifests/sota_followup/`; raw source-value logs, original repositories, models, and benchmark caches remain ignored. Dependency locks cover the new main, CDC, LUCARIO and Python3.7 Auto-Test runtimes. Rights are separate for code, data and pretrained artifacts.

Tested setup and arithmetic replay (repository working directory):

```bash
bash scripts/setup_sota_followup.sh
bash scripts/verify_sota_followup.sh
```

The setup script verifies cached public artifacts and uses pinned dependencies; the observed legacy TF1/NumPy metadata conflict remains documented. Setup was replayed in this existing machine, **not validated from a new empty cloud snapshot**. The independent replay regenerates ignored transformation logs from exact frozen operations, checks their SHA, verifies committed predictions, and runs52 tests; it does not claim fresh model inference.

Fresh original-model commands after setup (use paths, cwd and environment below) are in [04](04_original_model_reproductions.md). Fresh grid inference is `PYTHONPATH=src data/envs/sota/bin/python scripts/sota_ingest.py` in a **new output checkout**. Do not rerun it on the archived completed grid: it refits untouched models before checking per-case checkpoints. Preserve this archive and use a separate output version for changed code. Analyses can be replayed using `sota_analyze_ingest.py`, `sota_analyze_values.py`, `sota_diagnostic_analysis.py`, and `sota_write_reports.py` in the main runtime. Those are analyses of cached predictions, not new detector runs.
