# Dataset inventory

Audit date: 2026-10-26. Full-file acquisition, byte verification and scientific qualification are different states. No primary dataset currently passes every gate. Raw files, original values and review packets remain ignored under `data/`.

| Candidate | State | Reason |
| --- | --- | --- |
| raha_beers | CONDITIONAL | Every ounces value changes; ABV percent/fraction and N/A-to-empty conventions unresolved. Semantic precision cannot be asserted. |
| raha_flights | CONDITIONAL | Inter-source truth resolution; published reference not independently revalidated. Date/time parsing and imputed-truth lineage need original source follow-up. |
| raha_hospital | CONDITIONAL | 508/509 differences have an x-substitution signature. No cell-level injection lineage. Synthetic-pattern sensitivity, not verified natural errors. |
| raha_movies_1 | INCOMPATIBLE | Reference modifies IDs and derives correctness from duplicate labels; row identity and repair correctness not established. |
| raha_rayyan | CONDITIONAL | 722 date-field differences; date permutations, missing-to-minus-one references and uncertain repairs. Manual-source claim does not adjudicate this released pair. |
| raha_tax | CONDITIONAL | Postal leading zeros removed in reference; no stable row key. Large synthetic/reference-format population is not natural error evidence. |
| raha_toy | INCOMPATIBLE | Illustrative six-row fixture, unsuitable research sample. |
| cars | CONDITIONAL | 710 numeric representations and 110 generated missingness differences; descriptive Car is not a reliable unique key. Separate synthetic track only. |
| restaurant | CONDITIONAL | Generated missingness variant. Exclude class from features and scored cells; 125/155 differences remain. Only a separate synthetic ceiling check. |
| rt_bench | CONDITIONAL | Qualified technical subset; rights, conventional-control contract and independent grouping unresolved. Paper claims separate training corpora; release cannot independently verify source disjointness. |
| st_bench | CONDITIONAL | Qualified technical subset; rights, conventional-control contract and independent grouping unresolved. Paper claims separate training corpora; release cannot independently verify source disjointness. |
| uci_credit | PASS_SECONDARY | Original data acquired; outcomes are forbidden error labels. Source data not assumed pristine. |
| uci_bank | PASS_SECONDARY | Original data acquired; outcomes are forbidden error labels. Source data not assumed pristine. |
| holoclean_hospital | CONDITIONAL | Same underlying Hospital variant after explicit empty sentinel correspondence. Not an independent dataset. |
| holoclean_flight | CONDITIONAL | 57246 source rows with 2314 flight entities; reference keys are flight IDs, not positional row IDs. Separate entity-aware audit required. |
| rein_14_datasets | BLOCKED | Official checkout lacks main datasets directory. Linked ResearchGate endpoint returns HTTP 403. Ancillary example data are not a substitute for 14 labelled benchmark datasets. |
| holoclean_food_physicians | BLOCKED | Original paper describes partial manual annotation; selected official checkout does not release these full tables/annotation files. No fabricated or silently substituted labels. |

| Released pair | Rows × columns | Raw differences | Alignment evidence |
| --- | --- | --- | --- |
| raha_beers | 2410 × 11 | 4362 | POSITIONAL_WITH_ANCHORS |
| raha_flights | 2376 × 7 | 4920 | POSITIONAL_WITH_ANCHORS |
| raha_hospital | 1000 × 20 | 509 | POSITIONAL_WITH_ANCHORS |
| raha_movies_1 | 7390 × 17 | 7675 | POSITIONAL_ONLY_NOT_PROVEN |
| raha_rayyan | 1000 × 11 | 948 | POSITIONAL_WITH_ANCHORS |
| raha_tax | 200000 × 15 | 121219 | POSITIONAL_ONLY_NOT_PROVEN |
| raha_toy | 6 × 3 | 4 | POSITIONAL_ONLY_NOT_PROVEN |
| cars | 406 × 9 | 820 | POSITIONAL_ONLY_NOT_PROVEN |
| restaurant | 864 × 6 | 155 | POSITIONAL_ONLY_NOT_PROVEN |

29 acquired source files/archives are pinned by full SHA-256, URL, byte length and revision in [files.json](../manifests/files.json). Per-file schema, string storage, lexical missing tokens, distinct counts, duplicate rows and identifier uniqueness: [file_profiles.json](../evidence/file_profiles.json). CSV empty fields are preserved as empty strings; no claim distinguishes a true source NULL from an empty string without original metadata.

UCI Credit: 30,000 × 25; Bank additional full: 41,188 × 21. ZIP members and member hashes are recorded in [supplementary audit](../evidence/supplementary_audits.json). Full archives, not generated substitutes, were acquired. They provide no natural DQ labels. Official source pages explicitly state CC BY 4.0. Cite Yeh & Lien, DOI 10.24432/C55S3H; Moro et al., DOI 10.24432/C5K306.

Rights: Raha code Apache-2.0, HoloClean code Apache-2.0, dBoost GPLv3, CDC MIT (see pinned source-document hashes; verify downstream redistribution separately). Auto-Test has no top-level data/code licence located; bundled component licences do not license the whole release. Calgo LICENSE request returned 404. Public access is not blanket redistribution permission. No raw records or copyrighted PDFs are committed.

Recovery search followed Raha → HoloClean → REIN source dictionaries and original-paper Food/Physicians annotations → published generated Restaurant/Cars variants → UCI. Food/Physicians were not present in the selected official release. ResearchGate returned 403; no access bypass was attempted. A guessed HoloDetect GitHub location returned repository-not-found and is not treated as an authoritative missing-data claim. This is a bounded search, not evidence that no suitable benchmark exists.

HoloClean Hospital is the same underlying release as Raha Hospital: 19,000/19,000 clean values correspond after the explicitly observed empty-string ↔ `empty` convention; dirty values also match under that correspondence. They are not independent samples. HoloClean Flights has 57,246 rows, 8 fields and 2,314 flight entities; it must not be mistaken for the 2,376 × 7 Raha variant. Checksums also reveal byte-identical material in previous pilots; these sources are exploratory, not pristine holdouts.
