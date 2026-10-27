# Published references: matched units and pretraining

| benchmark | method | eligible_values | reference_positives | hits | alerts | ambiguous_alerts |
| --- | --- | --- | --- | --- | --- | --- |
| rt | R | 90934 | 41 | 0 | 0 | 0 |
| rt | RS | 90934 | 41 | 4 | 3142 | 5 |
| rt | riolu_original | 45136 | 3 | 3 | 4622 | 1 |
| rt | riolu_small_sample | 90656 | 41 | 19 | 11239 | 19 |
| rt | lucario_transductive | 89521 | 41 | 5 | 1289 | 7 |
| rt | AutoTest_pattern_only_rt_train | 90934 | 41 | 3 | 130 | 7 |
| rt | AutoTest_pattern_only_st_train | 90934 | 41 | 3 | 35 | 6 |
| rt | AutoTest_pattern_native | 90934 | 41 | 3 | 13 | 3 |
| rt | AutoTest_full | 90934 | 41 | 10 | 35 | 10 |
| st | R | 71719 | 45 | 0 | 0 | 0 |
| st | RS | 71719 | 45 | 6 | 2872 | 8 |
| st | riolu_original | 29866 | 4 | 4 | 5334 | 5 |
| st | riolu_small_sample | 69790 | 45 | 28 | 17413 | 58 |
| st | lucario_transductive | 69902 | 42 | 14 | 1010 | 17 |
| st | AutoTest_pattern_only_rt_train | 71719 | 45 | 9 | 191 | 19 |
| st | AutoTest_pattern_only_st_train | 71719 | 45 | 4 | 174 | 11 |
| st | AutoTest_pattern_native | 71719 | 45 | 4 | 16 | 6 |
| st | AutoTest_full | 71719 | 45 | 6 | 23 | 8 |

Standalone coverage differs by method. Values from failed/inapplicable columns are null, not converted to clean. Default RIOLU supports74RT/46ST columns before the LUCARIO intersection; the strict U0 common cohort is73RT/46ST. On that cohort RS already finds all 3/4 positives; original RIOLU adds 0 beyond RS. This is a real negative matched result, not evidence that its unsupported small columns are clean.

| benchmark | cohort | method | values | positives | hits | extra_hits_beyond_RS | extra_alerts_beyond_RS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rt | U0_original_RIOLU_supported | RS | 44519 | 3 | 3 | 0 | 0 |
| rt | U0_original_RIOLU_supported | riolu_original | 44519 | 3 | 3 | 0 | 3040 |
| rt | U0_original_RIOLU_supported | lucario_transductive | 44519 | 3 | 2 | 0 | 523 |
| rt | U0_small_sample_adaptation | RS | 89243 | 41 | 4 | 0 | 0 |
| rt | U0_small_sample_adaptation | riolu_small_sample | 89243 | 41 | 19 | 15 | 9035 |
| rt | U0_small_sample_adaptation | lucario_transductive | 89243 | 41 | 5 | 2 | 1216 |
| rt | U2_same_corpus_native_policy | RS | 90934 | 41 | 4 | 0 | 0 |
| rt | U2_same_corpus_native_policy | AutoTest_pattern_native | 90934 | 41 | 3 | 2 | 9 |
| rt | U2_same_corpus_native_policy | AutoTest_full | 90934 | 41 | 10 | 8 | 28 |
| st | U0_original_RIOLU_supported | RS | 29866 | 4 | 4 | 0 | 0 |
| st | U0_original_RIOLU_supported | riolu_original | 29866 | 4 | 4 | 0 | 4383 |
| st | U0_original_RIOLU_supported | lucario_transductive | 29866 | 4 | 2 | 0 | 319 |
| st | U0_small_sample_adaptation | RS | 67973 | 42 | 6 | 0 | 0 |
| st | U0_small_sample_adaptation | riolu_small_sample | 67973 | 42 | 28 | 22 | 15147 |
| st | U0_small_sample_adaptation | lucario_transductive | 67973 | 42 | 14 | 10 | 773 |
| st | U2_same_corpus_native_policy | RS | 71719 | 45 | 6 | 0 | 0 |
| st | U2_same_corpus_native_policy | AutoTest_pattern_native | 71719 | 45 | 4 | 2 | 12 |
| st | U2_same_corpus_native_policy | AutoTest_full | 71719 | 45 | 6 | 4 | 17 |

The small-sample RIOLU adaptation expands applicability and adds 15RT/22ST publisher-positive values beyond RS in its LUCARIO-matched cohort, at 9035/15147 extra alerts. Full Auto-Test adds 8RT/4ST beyond genericRS with 28/17 extra alerts over the full eligible universe. Its U2 pretrained artifacts are a substantial information difference; no same-information U0 superiority claim is made. Native pattern ablation versus full shares the released corpus/reporting policy. Value-level precision excludes ambiguous values from the denominator while including their reviews in cost; no row reconstruction or global F1.

Auto-Detect:44 released method/rank strata contain4339 parsed judgments, 4006 distinct candidate pairs. Thirty pairs have conflicting labels including ambiguity;19 conflict directly0versus2. Original Auto-Detect sampled-stratum precisions excluding ambiguous are1.000,.9865,.9368,.9753 for0–100,100–200,200–500,500–1000. These are conditioned candidate measurements; no exhaustive recall, full population precision or new method execution. NonUTF8 bytes are preserved via Latin1 mapping and actual newline bytes, not Unicode splitlines.

Hospital/Beers remain historical reference-agreement sensitivities with no new claim of semantic adjudication. Hospital copies and RIOLU's fixture do not provide additional independent sources. No modern detector is declared universal winner across these incompatible units/regimes.
