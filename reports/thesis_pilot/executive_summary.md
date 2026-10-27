# Executed empirical pilot

**CONDITIONAL GO for a bounded empirical MSc thesis; no operational AI-adoption claim.** Unlike the initial audit, this branch contains executed models and paired experiments. The original audit/manifests/reports remain preserved.

Primary results cover four predeclared fields per source, 800 evaluation rows per source and at most 2,400 historical training rows. Full archives were acquired. This is substantial exploratory evidence, not an exhaustive all-field benchmark, a final confirmatory thesis or a production-bank validation.

| Dataset | Primary scenarios | History rows | Evaluation rows | Evaluated fields |
| --- | --- | --- | --- | --- |
| credit | 225 | 2399 | 800 | AGE, LIMIT_BAL, BILL_AMT1, EDUCATION |
| bank | 225 | 2400 | 800 | age, duration, previous, job |
| wine | 180 | 1954 | 800 | alcohol, density, pH, sulphates |

Final primary grid: **630 unique cell-intervention scenarios**, ECAR/EAR/ENAR 210 each; E1 missing 135, E2 datatype 135, E3 code 90, E4 ×10 scale 135, E5 plausible substitution 135. Three prevalence settings (1/5/10% of the eligible target column), five seeds. There are **52,740 metric rows**, not 52,740 independent experiments. A separate **45-scenario Bank cross-field row track**, **18 full-feature scope probes**, **18 source-type CDC diagnostics**, two published-reference tables and eight synthetic linked-table cases were executed.

Main findings:

- Basic and extended controls detect every injected stipulated E1/E2/E3 violation in the 360 relevant primary scenarios. No detector can add unconstrained true hits beyond this complete coverage for these narrowly defined families.
- CDC's native configuration sometimes adds substantial **alteration-reference hits**, with high extra alert burden. For ECAR at 5%, Credit substitution adds 28.6/40 changed cells on average beyond B, but 1,124.2 extra cell alerts per 800-row batch. Those are matched altered values, not newly proven semantic data errors.
- At a shared review capacity, gains can shrink or become negative. Control priority and fusion policy matter. A provenance-based hard-rule-priority sensitivity is reported separately from the predeclared binary-hash policy.
- Original LUCARIO including regex inference was reproduced, with exact 20,000-cell flag parity on the authors' Hospital example. Original CDC, original dBoost, a separately named ExtraTrees predictor and original Raha learning stages were executed. Raha receives 20 labelled rows and is never pooled with label-free methods.
- Publisher-reference tests can show complementary hits, but Hospital's x-substitution signature and Beers' representation changes prevent general natural-error claims.
- Local Qwen3-0.6B Q8_0 ran locally. After one prompt-interface repair, 4 schema-only candidates yielded 2 stipulated baseline duplicates and 2 repetitions of explicit source-schema types, not evaluated as detector additions; 0 were rejected. Age's already stipulated bound and unimplemented integer checks were corrected in the semantic validator, preserving its prior classification. The initial four ambiguous candidates and underspecified unary-parameter interface are preserved. No generated rule was promoted or evaluated as an incremental detection benefit.

Verification: **43 tests passed in the pilot environment**, 205,093 primary independent arithmetic/identity checks, and 52,505 supplemental checks. This is independent software implementation, not independent human semantic adjudication. Original lightweight audit environment separately passes 29 tests with the new optional pilot module skipped.

Engineering: dataset registration, source hashing, contracts, A/B rules, four selectable detector adapters, findings and bounded recommendations execute locally. A generic registered-source intervention command also executes on a copy: 9 verified type violations, original source unchanged. The synthetic demonstration finds its two existing known schema violations; the source scan returns INSUFFICIENT_EVIDENCE without real labels. See [final recommendation](final_recommendation.md).
