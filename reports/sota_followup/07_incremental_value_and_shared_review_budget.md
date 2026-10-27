# Increment, alerts and shared review cost

Primary descriptive numeric panel: full context, ECAR5%, mean of five paired seeds, 40 altered targets per case except Credit wrong-period (36 changes from 734 eligible non-noop rows). Extra counts are beyond **RSM with numeric Ridge**; net is at 20 shared cell reviews (25 per 1000 rows). Those changes are transformations, not independently confirmed semantic errors.

| dataset | family | mean_extra_hits | mean_extra_alerts | mean_net_hits |
| --- | --- | --- | --- | --- |
| bank | P1_context_donor | 2.2 | 509 | 0 |
| bank | P4_valid_category | 20.6 | 522 | 0.4 |
| bank | P6_systematic_offset | 17.8 | 508 | 0.2 |
| credit | P2_wrong_period | 0.6 | 676 | -0.2 |
| credit | P4_valid_category | 11.4 | 682.6 | 0 |
| wine | P1_context_donor | 12.8 | 903.6 | -1 |
| wine | P3_scale_099 | 0 | 855.8 | -1.6 |
| wine | P3_scale_101 | 0 | 856.6 | -1.6 |

CDC's larger unions often add hundreds of alerts per few extra changed values. For Wine scale changes there is0 new unconstrained coverage; net reviewed changes can still vary because overlapping detector flags alter review priority. A positive reviewed net is not necessarily a newly detectable error. All four methods, both views and all mechanisms/rates are in `ingest_summary.csv`; baselinesR/RS/RSM remain separately visible.

The categorical-M gap matters. Adding a cheap history-calibrated logistic comparator changes the full-context ECAR5% valid-category result under20 reviews:

| dataset | baseline | net_hits | lost_hits |
| --- | --- | --- | --- |
| bank | RSM_LR95 | -0.4 | 0.6 |
| bank | RSM_LR995 | 0 | 0.2 |
| credit | RSM_LR95 | -0.2 | 0.2 |
| credit | RSM_LR995 | -0.2 | 0.2 |

The .95 comparator removes CDC's apparent Bank budget benefit (mean net−.4);.995 gives0. Both cutoffs are declared/reported, no favorable one chosen from labels. Credit is−.2 for both. Confidence/ablation choices discovered here remain exploratory.

`counterpart_increment.csv.gz` distinguishes newly triggered extra hits from previously flagged source cells. Example Bank age+1: CDC has 17.8 extra hits beyond RSM, but8.8 newly triggered and 9already flagged on the original source. Bank category:20.6 extra, 18.4 newly triggered; Wine donor12.8 extra, 9.4 newly triggered. Newly triggering suspicion is not an independent semantic error label.

RT/ST use fixed25/50/100 distinct-value reviews, plus1/2.5/5% applicable-value sensitivity. A value review is not a row review. At25 totalreviews, fullAutoTest+genericRS equal-share gains5RT/4ST; generic-control-first yields 0/0 because the RS queue exhausts capacity. Native-ranked equal-share gives5RT/6ST. Ambiguous alerts consume slots. Stronger source-corpus pattern priority yields:

| benchmark | baseline_hits | union_hits | net_hits | reviewed | ambiguous_reviews |
| --- | --- | --- | --- | --- | --- |
| rt | 3 | 6 | 3 | 25 | 5 |
| st | 4 | 5 | 1 | 25 | 8 |

These are exploratory priority sensitivities without label-based ranking. The pattern-first comparator already finds 3/4 positive values, leaving only 3/1net additional. Do not present5/4 as gain beyond established semantic-domain controls. Binary detectors receive hash order, not invented confidence; only native Auto-Test FPR-derived scores get native-ranked sensitivity. Hard R findings are always first in all numeric schedules; generic S is not a hard contract.

P5 ECAR5%: RIOLU dates40changed hits/40alerts, 20 reviewedhits at 20capacity; ipv4 40/82.2,7.6 reviewed; codes.4/13.6,.4 reviewed (zero newly triggered change hits). LUCARIO codes40/86,9.4 reviewed; dates1/3.2,1 reviewed; ipv4zero. AutoTest RTpattern-onlyzero in these transfers. These gains are against coarse label-free profiles without supplied format contracts, not proof of advantage over a known date/IP parser or enterprise rules. Where the true snapshot is available, reconciliation wins completely.

Resource costs are observed computation/review counts, not monetary savings. Full native Auto-Test RT 245.35sec and ST 289.38sec; exact wall/RSS fields are in per-run JSON. RSS is process/maximum-child, not aggregate simultaneous memory. RIOLU/LUCARIO per-column timings and 10sec resource failures are retained. Main fit and per-case wall times are saved; full-system peakRSS for every method was not instrumented and is not invented. Local ZeroED logs five calls per attempt/10 total, per-call seconds and 700maxnewtokens; max tokens is a cap, not measured generated tokens or user annotation time.

Source-stratified conditional group sensitivity resamples frozen duplicate-feature groups within each source with 300 resamples; seeds are paired sensitivity replications, not independent datasets. No source-general confidence interval or pooled enterprise effect is claimed.
