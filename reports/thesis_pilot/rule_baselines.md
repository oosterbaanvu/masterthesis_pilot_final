# Rule baseline provenance and applicability

A/B configurations and per-column provenance: `results/thesis_pilot/*_contracts.json`. The separate `manifests/thesis_pilot/rule_provenance.json` enumerates each applied primary control, its own provenance, parameters and evidence; this separates stipulated requiredness from documented categorical domains. A is not intentionally weakened. Every evaluated cell has an explicit operational requiredness and datatype/category contract. B includes all A findings; the code and tests assert A ⊆ B for unconstrained alert sets.

| Layer | Controls | Provenance and limits |
| --- | --- | --- |
| A | Explicit requiredness; finite numeric parsing; accepted category codes; justified/stipulated physical bounds | Requiredness generally EXPLICIT_STIPULATED_CONTRACT. Bank category lists DOCUMENTED_SOURCE_CONTRACT. Credit code acceptance is deliberately permissive. Wine bounds use an explicit operational convention. |
| B | A plus 0.5/99.5% history quantiles, 3-IQR robust bounds, category-share threshold 0.005, conditional Ridge residual threshold calibrated on the last quarter of history | TRAINING_ONLY_STATISTICAL_CONTROL, not semantic business truth. Ridge α=10 and thresholds are frozen independently of evaluation interventions. |
| Row E6 | previous=0 iff poutcome=nonexistent, with lexical/domain controls and statistical row alerts | EXPLICIT_STIPULATED_CONTRACT motivated by Bank campaign semantics; verified on untouched approved rows before mutation. Findings are rows, not blame assigned to every participating cell. |
| Linked-table fixture | Unique IDs, parent references, status enum, integer cents, expected deliveries, debit/credit and source/ledger totals | EXPLICIT_STIPULATED_CONTRACT on explicitly synthetic data. |

Conditional linear residual monitoring makes B broader than univariate thresholds. It is still a research approximation of available conventional controls, not a certified mature bank suite. Single-source UCI tables do not contain account/transaction parents or legitimate ledger totals: those checks are NOT_APPLICABLE in the primary cell track and executed in the linked fixture instead. The full Bank relation is evaluated in its separate row track. No dependency is invented from correlation alone.

Numeric lexical validity is checked before bounds; INVALID_NUMERIC and NaN cannot silently bypass range rules. IDs/postcodes/phone strings are never generically normalised as numbers in external data. Statistical preprocessing of numeric model features can impute unparseable values, but this is explicit; the ExtraTrees residual adapter abstains on an invalid numeric target rather than claiming to infer its semantic correctness.

Budget policies matter: adding statistical alerts increases the unconstrained superset but can consume review capacity. The primary binary-hash policy remains reported. `review_priority_sensitivity.json` separately puts A's hard-contract alerts before B's statistical suspicion, then combines remaining candidates without test-label priority. This is a post hoc provenance-policy sensitivity, not retrospective threshold tuning.
