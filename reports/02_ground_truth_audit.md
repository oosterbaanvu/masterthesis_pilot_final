# Ground-truth audit

No independent semantic adjudication has occurred. Automated pattern checks establish reproducible properties of references, not which source value is true. The operational statuses are:

- VERIFIED_REFERENCE_ERROR: independent authoritative evidence identifies the original as wrong for the specified task. **Zero assigned.**
- CONTROLLED_INJECTION_ERROR: requires a traceable generated change **and an independently stipulated violated contract**. No acquired source currently meets both requirements, so zero assigned. Published `?` alterations alone lack a qualified requiredness contract. Class/outcome fields are excluded from future experiments.
- REPRESENTATION_ONLY: exact finite Decimal equality on an explicitly numerical field. Identifiers, postal codes and telephone numbers never use this rule. Numeric equivalence does not certify units or business meaning.
- DEBATABLE_OR_UNCERTAIN: source disagreement without sufficient semantic adjudication, including unit contracts, repaired sentinels, date permutations and reference loss of identifier zeros.
- UNVERIFIED_REPAIR: explicitly documented automatic repair with no independent correctness evidence. No acquired pair was assigned here without such lineage.
- NOT_AN_ERROR: literal agreement with supplied reference only; operational negative in a reference-relative target, **not proof of semantic cleanliness**.
- UNKNOWN: unavailable label/value/identity prevents an interpretation. Missing Auto-Test arrays trigger whole-column exclusion rather than becoming empty annotations.

| Pair | Raw differences | Numeric representation only | Generated missingness candidates (not verified errors) | Uncertain | x-substitution candidates |
| --- | --- | --- | --- | --- | --- |
| raha_beers | 4362 | 0 | 0 | 4362 | 0 |
| raha_flights | 4920 | 0 | 0 | 4920 | 0 |
| raha_hospital | 509 | 0 | 0 | 509 | 508 |
| raha_movies_1 | 7675 | 669 | 0 | 7006 | 0 |
| raha_rayyan | 948 | 0 | 0 | 948 | 0 |
| raha_tax | 121219 | 87342 | 0 | 33877 | 0 |
| raha_toy | 4 | 0 | 0 | 4 | 0 |
| cars | 820 | 710 | 110 | 110 | 0 |
| restaurant | 155 | 0 | 155 | 155 | 0 |

Hospital: 508/509 changes have equal-length positions differing only by substitution to `x`. This supports a synthetic-pattern diagnosis, not a reconstructed corruption log. Score and sample fields include textual values; globally coercing them to numbers would be wrong. Beers: all 2,410 ounces values change, 1,005 IBU cells, 693 ABV cells, and 127 each city/state. `12.0 oz` versus `12` is a representation candidate, conditional on the unit contract; `0.09%` versus `0.09` is scale-ambiguous. N/A versus empty is not automatically a true error. Rayyan: 722/948 differences are date-field changes; date order is not guessed. Tax: 87,342 finite numeric equivalents are separated, while 31,311 postal-zero changes remain uncertain rather than being silently erased. Movies changes IDs and derives truth from duplicate labels (Raha §6.1); neither reference identity nor repair correctness is established.

The raw schema names differ for Hospital, Beers and Movies. Exact, versioned schema correspondences are in `configs/schema_maps.json`; an unregistered schema fails closed. Positional equality plus an unchanged unique index anchors some pairs but does not prove absence of all entity shifts. Tax/Movies lack a proven stable alignment. HoloClean reference keys are audited separately: Hospital `(row tid, attribute)`; Flights `(flight entity, attribute)`. Reference key coverage is not equivalent to a verified correct value.

| Column benchmark | Physical records | Empty records | Eligible columns | Excluded columns | Eligible distinct values | Published obvious errors | Debatable |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rt_bench | 1048575 | 1047375 | 1194 | 6 | 90934 | 41 | 35 |
| st_bench | 1200 | 0 | 1193 | 7 | 71719 | 45 | 77 |

RT has six count mismatches; ST has four count mismatches, two absent value arrays and one invalid annotation expression (`['refridgerator'+C1187]`). Exact indices and reasons are in `evidence/column_audits.json`. No expression is evaluated as code. Exclusions preserve the benchmark's original bytes and are not asserted to fix its annotation semantics. There is no fabricated occurrence frequency or row reconstruction. The eligible benchmark retains published unambiguous/debatable labels separately; these are publisher judgments, not new verified human annotations by this study.

Traceable stratification: up to three changes for every observed (column, status) stratum, deterministic ascending row order; this is an audit sample, not a random prevalence estimator. Local `data/derived/*_sample.json` includes original/reference, coordinates, interpretation and reason; `*_labels.csv` contains every disagreement. Blind review packets omit our status/reason and include blank decision/evidence fields. Reviewers should independently judge correctness and cannot-judge against original source conventions, then reconcile conflicts. No review scores or inter-rater agreement are invented. These raw-value packets are intentionally not redistributed in Git.
