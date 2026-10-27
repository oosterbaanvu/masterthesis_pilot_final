# Executed local Data Quality Evaluation Service

Python package: `dq_service`, entrypoint **dqeval** (or `python -m dq_service`). The artifact is a local CLI/research service, not an HTTP deployment or frontend.

Supported path: register a CSV+schema contract → pin its source hash → load separate historical values → run A/B controls → run a compatible detector adapter → write coordinate findings and machine-readable report → return a bounded recommendation. A changed registered source hash fails instead of silently refreshing provenance. Declared outcome/reference feature names are rejected. Wrong feature alignment, invalid numeric strings and incompatible target units have negative tests.

Selectable scan adapters: contextual_extra_trees, original dBoost text, original LUCARIO history inference and original CDC. Separate environments preserve incompatible Python/library requirements. A native failure leaves control results available and records BLOCKED_TECHNICAL rather than fabricating zero model alerts. Native source/rights and information caveats still apply.

The generic `experiment` command supports registered-source missing/type/code/scale/substitution interventions using official ECAR/EAR/ENAR placement, separate history, A/B and contextual ExtraTrees, untouched counterfactuals, review budgets and machine-readable outputs. It writes a dirty copy and local value log without changing the registered file. The executed synthetic type demo creates 9 new violations among 199 eligible rows; ExtraTrees explicitly abstains on unparseable numeric targets. Scale/substitution are labelled alterations. This service demonstration is separate from the 630 primary scenarios.

Actually executed demo: 200 explicitly synthetic transactions, 40 accounts and a paired-entry ledger. Eight mutations exercise missing parents, duplicate IDs, invalid status, missing delivery, imbalance, source/ledger mismatch, requiredness and numeric validity. Untouched fixture passes its stipulated invariants. Registration and scans executed with both ExtraTrees and original dBoost. The two known lexical/domain violations are found by basic controls; additional statistical findings remain suspicion. The unlabeled scan returns INSUFFICIENT_EVIDENCE, not adoption based on alert volume.

```
bash scripts/setup_thesis_pilot.sh
PYTHONPATH=src data/envs/pilot/bin/python scripts/engineering_fixture.py
data/envs/pilot/bin/dqeval --help
# Generic new-source contract registration and scan:
data/envs/pilot/bin/dqeval register --id my_source --csv /path/new.csv --contract /path/contract.json
data/envs/pilot/bin/dqeval scan --id my_source --history /path/history.csv --output /path/findings --detector contextual_extra_trees
# Generic intervention evaluation on a copy of that registered source:
data/envs/pilot/bin/dqeval experiment --id my_source --history /path/history.csv --target amount --family type --rate .05 --output /path/experiment
# Full scientific reproduction (checkpointed, labels/scopes explicit):
bash scripts/reproduce_thesis_pilot.sh
```

Recommended source layout is the existing checkout; every cloud task is already isolated, so do not create a Git worktree. Source caches, original data, local injection-value logs and fitted weights remain ignored. Package locks and source revisions are committed; `setup_thesis_pilot.sh` was executed successfully against the prepared environment. Fresh-instance cloud restoration has not been verified.

Local LLM: Qwen/Qwen3-0.6B-GGUF revision 23749fefcc72300e3a2ad315e1317431b06b590a, Q8_0 SHA-256 9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031, local llama.cpp completion, temperature 0, seed 42, 2 CPU threads, 28.18 seconds. Public schema only, no private records, labels or paid APIs. After one prompt-interface repair, 4 schema-only candidates yielded 2 stipulated baseline duplicates and 2 repetitions of explicit source-schema types, not evaluated as detector additions; 0 were rejected. Age's already stipulated bound and unimplemented integer checks were corrected in the semantic validator, preserving its prior classification. The initial four ambiguous candidates and underspecified unary-parameter interface are preserved. No generated rule was promoted or evaluated as an incremental detection benefit. This is neither Qwen3-8B evaluation nor original ZeroED reproduction. Optional build/acquisition/generation scripts and logs remain separate from the core study.

`dq_service.recommend` supports ADOPT / DO_NOT_ADOPT / INSUFFICIENT_EVIDENCE only under explicit scope, semantic-reference and review-cost prerequisites. Current pilot outputs support bounded DO_NOT_ADOPT for already covered stipulated schema families and INSUFFICIENT_EVIDENCE for broad operational adoption. Test fixtures exercising an ADOPT branch are policy tests, not empirical adoption evidence.
