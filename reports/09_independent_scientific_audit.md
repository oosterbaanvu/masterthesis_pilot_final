# Adversarial scientific audit

An independently coded counting script (`scripts/verify_independently.py`) does not import the production audit package. It reopens original bytes, recomputes all pair disagreement counts, verifies every saved sample's coordinates/values, reconstructs eligible RT/ST counts and exclusions and checks manifest hashes. This is independent computational implementation, **not an external examiner or human semantic annotation**. Full outcomes: `evidence/independent_checks.json`. Unit and deliberate negative leakage tests: `evidence/pytest.log`.

Challenges and conclusions:

1. Is every difference an error? No: 710 Cars and 87,342 Tax numeric equivalents demonstrate otherwise; postal zeros and ABV units remain uncertain. No semantic VERIFIED_REFERENCE_ERROR was assigned.
2. Are repeated dataset versions independent? No: HoloClean/Raha Hospital correspondence is exact after a documented missing-token representation mapping. Different filenames/hashes do not establish independent data.
3. Same task/information? No: CDC clean history, Raha user labels, dBoost dirty-table fitting and Auto-Test offline corpus differ. The compatibility matrix blocks a pooled leaderboard.
4. Train/test leakage? No experiment was fitted here, hence no claimed experimental leakage-free outcome. Tests reject known reference columns, wrong roles and unapproved schemas. These structural guards cannot detect a maliciously renamed reference value. Dataset-wide inspection means these sources cannot now be called unseen confirmation data.
5. Baseline deliberately incomplete? A missingness-only Hospital or RT/ST baseline would not represent mature enterprise controls. No credible extended primary baseline is accepted; the pipeline stops rather than manufacturing AI gain.
6. Dependent measurements? Distinct values in columns and columns from unknown sources are dependent. Two exact cross-benchmark header/value fingerprints overlap. Without source metadata, inferential source-cluster claims remain blocked.
7. Faithful implementation? Original dBoost fixture works, but its minimal output is row-level. CDC/Auto-Test full runs were not reproduced; no proxy or approximate detector is presented as faithful.
8. Detection versus repair? HoloClean precision in its paper evaluates correct repairs; it is not interchangeable with our proposed detection task. Flights entity conflicts and Movies duplicate-derived truth have unresolved semantic attribution.
9. Valuable null result? Yes in the proposed protocol: zero extra hits or displaced control hits are reportable. No such experimental result has yet been measured.

Supported claims: exact acquired-byte properties, explicit reference disagreements, conservative structural eligibility, version relationships, tested guard/metric behaviour and limited upstream fixture execution. Unsupported: independent semantic correctness, commercial data permission, completed novelty, fair detector superiority, incremental performance or generalisation to bank production.

Readiness check states: clean acquisition/integrity/alignment diagnostics/label-schema/compatibility guards/leakage negatives/baseline guards executed. Benchmark baseline sanity and main metric reproduction are NOT_EXECUTED, because there is no admitted primary experiment. Human annotation is NOT_EXECUTED. Report-number checks operate on saved audit outputs, not imaginary model results. Unit passes do not establish scientific validity.
