# Repair and retest log

Full machine-readable register: [issues.json](../manifests/issues.json). `RESOLVED_CONDITIONALLY` is not an all-clear. Evidence contains failed attempts and successful retests.

| ID | Severity | Root cause | Repair / status | Verification |
| --- | --- | --- | --- | --- |
| I01 | MAJOR | Spreadsheet-export padding and invalid/missing list values | Filter fully empty records; parse literals safely; exclude exact invalid columns — RESOLVED_CONDITIONALLY | independent_column_recount |
| I02 | MAJOR | Different reference header names | Pin explicit ordered schemas; fail on drift — RESOLVED_VERIFIED | schema guards and raw recount |
| I03 | CRITICAL | Published discrepancy is not necessarily semantic error | Separate representation/uncertainty and generate review packets — INTRINSIC_LIMITATION | no_unearned_semantic_certification |
| I04 | MAJOR | Reference tid contains flight entity keys, not integer row IDs | Separate entity-key audit instead of integer cast — RESOLVED_CONDITIONALLY | 2314 source/reference entities, zero absent |
| I05 | CRITICAL | Clean-history/calibration assumptions incompatible with dirty-only primary track | Separate information track; do not approximate published algorithm — INTRINSIC_LIMITATION | compatibility negative tests |
| I06 | CRITICAL | No overall release/data permission established | Preserve local files; no raw redistribution; require rights clarification — BLOCKED_EXTERNAL | review source documents and 404 licence response |
| I07 | CRITICAL | Extended source-authoritative baseline not qualified | Specify contracts and freeze after metadata/expert review — OPEN | rule guard tests only; benchmark sanity NOT_EXECUTED |
| I08 | CRITICAL | Hidden source identity/corpus overlap cannot be independently checked | Fingerprint visible columns; separate paper disjointness claim from verification — BLOCKED_EXTERNAL | two exact cross-benchmark overlaps |
| I09 | MAJOR | Closest work already studies complementarity | Read Auto-Test §6.6 and 2016 comparison; narrow proposed contribution — RESOLVED_CONDITIONALLY | official PDFs acquired and text inspected |
| I10 | MAJOR | No main datasets directory; external link denied or full labels not released | Inspect dictionary/official examples and seek original manual benchmark alternatives — BLOCKED_EXTERNAL | ResearchGate 403; no substitution |
| I11 | MINOR | Initial network proxy rejected required hosts | Add only required official domains and retry after runtime change — RESOLVED_VERIFIED | official PDF/ZIP successful downloads |
| I12 | MAJOR | Empty versus empty-string causes false distinct-dataset inference | Check all 19000 cells with explicit sentinel correspondence — RESOLVED_VERIFIED | raha_clean_matching_after_empty_mapping=19000 |
| I13 | MINOR | Second-pass server 502 after successful original acquisition | Preserve failed attempt; retry only missing files against same hash — RESOLVED_VERIFIED | evidence/clean_acquisition.json |
| I14 | MAJOR | Native minimal CLI outputs row indices and parser may discard invalid types | Original-code fixture; block claimed cell adapter readiness — RESOLVED_CONDITIONALLY | original fixture detected row 100 |

Observed failed attempts preserved: initial public-paper network 403 before permitted-domain update; nonexistent guessed Flights PDF yielded HTML, rejected by pdftotext; Calgo README-linked notebook/benchmark paths returned 404; no code or labels inferred from those missing links; first audit refused differing schemas before explicit mappings; first HoloClean audit wrongly attempted integer conversion of flight IDs, corrected to entity semantics; initial UCI repeat requests returned 502, then identical-hash reacquisition succeeded. Audit-policy amendment v0.2: generated missingness without an independently justified requiredness contract is now uncertain, not CONTROLLED_INJECTION_ERROR. Superseded counts are preserved in evidence/superseded_pair_audit_v0.json; current labels/reports were regenerated and independently recounted. No detector performance results preceded these repairs, so none were silently retained under changed label policy.

A manually launched verification once overlapped artifact regeneration and failed the Cars label recount; the failed attempt is preserved in evidence/verification_attempt_during_regeneration.json. Final verification is serialized after audit completion, as in scripts/reproduce.sh.

No final holdout labels were used to repair a fitted model: there was no fitted benchmark experiment. Whole-benchmark qualification exposure is nevertheless disclosed, and these public sources remain exploratory.
