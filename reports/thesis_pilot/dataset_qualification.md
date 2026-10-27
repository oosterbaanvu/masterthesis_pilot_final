# Dataset qualification by evaluation track

Primary intervention sources are fully acquired: Credit (30,000 × 25 raw fields including ID/outcome), Bank additional full (41,188 × 21) and White Wine (4,898 × 12). Archive/member identities, immutable byte hashes and UCI source URLs are in `manifests/thesis_pilot/datasets.json`. UCI pages describe CC BY 4.0; attribution remains required. Original bytes are unchanged and ignored. Prediction outcomes default-payment/y/quality and Credit ID are excluded from model features and error labels.

| Dataset | Primary scenarios | History rows | Evaluation rows | Evaluated fields |
| --- | --- | --- | --- | --- |
| credit | 225 | 2399 | 800 | AGE, LIMIT_BAL, BILL_AMT1, EDUCATION |
| bank | 225 | 2400 | 800 | age, duration, previous, job |
| wine | 180 | 1954 | 800 | alcohol, density, pH, sulphates |

These sources pass acquisition, shape, duplicate-group separation and **track-specific intervention** checks. None is certified globally clean. Unknown source anomalies are not manufactured negatives. Permissive Credit category contracts preserve the known undocumented/exceptional education/marriage/payment codes; those observed exceptions are not declared naturally erroneous. Bank `unknown` and `pdays=999` remain legitimate source conventions. No unsupported rule declares all `pdays=999` rows to have previous=0. Wine concentrations and percentage/pH bounds are explicit operational stipulations, not all copied as publisher-provided business rules.

The primary four-column views support a coherent common unit, but do not exhaust all available cross-field information. The separately executed full-feature probes supply all 23/20/11 non-outcome input fields to both the conditional baseline and contextual models, retaining the same four scored fields. They are sensitivity evidence, not additional datasets.

External Hospital and Beers were executed on publisher-reference differences. Hospital/Raha and HoloClean variants are related, not independent replications. Flights remains a conditional multi-source/entity-keyed candidate; it was not silently scored with incompatible row references. RT/ST remain distinct-column/value benchmarks with the original audit's 1,194/1,193 eligible columns. No relational rows or occurrence counts were invented. Full Auto-Test inference was not reproduced. REIN's primary external files remained access-limited; its paper is now acquired and reviewed through arXiv:2302.04702v1.

Synthetic accounts/transactions/ledger/reference relationships are engineering fixtures only. Their eight mutations test stipulated contracts; they do not add a fourth independent real source or support real financial prevalence/generalisation claims.
