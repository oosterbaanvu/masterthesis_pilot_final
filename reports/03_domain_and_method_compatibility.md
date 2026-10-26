# Method × dataset × label compatibility

Full matrix: [compatibility.json](../manifests/compatibility.json). Status is scientific compatibility, not a successful installed run. No common leaderboard is valid across the following information regimes.

| Method / pinned source | Output | Fit information | Runtime and constraints | Decision |
| --- | --- | --- | --- | --- |
| CDC / se-jaeger | Cell membership in conformal set/interval; ranking not assumed | Published paper assumes clean history plus calibration; not error-labelled fitting | Python >=3.9,<3.10; AutoGluon 0.8.2; sklearn<1.3; substantial per-column fits; MIT | CONDITIONAL separate clean-history track; NOT_EXECUTED |
| dBoost / cpitclaudel | Native discrepancies localizable to expanded fields; minimal CLI emits row IDs | Dirty table transductive or separate history; Gaussian/histogram thresholds user-configured | Original upstream code executes on fixture; GPLv3; float-first parser may discard later malformed values | CONDITIONAL cell adapter; never label minimal CLI row output as cells |
| Raha / BigDaMa | Cell flags | Iterative labelled tuples; transductive clustering/label propagation; optional history | Apache-2.0; user labels count toward review budget, must avoid clean-path oracle | CONDITIONAL separate labelled-reference track; NOT_EXECUTED |
| Auto-Test SDC | Distinct values within a column; published confidence | Pretrained cross-table corpus; dirty test column context | Published legacy Python 3.7/TensorFlow1 setup, models external Drive; no overall release licence found | CONDITIONAL column/value only; NOT_EXECUTED |
| Isolation Forest | Row score | Dirty training rows, train-only preprocessing | Additional established method reviewed; row anomaly is not localized DQ error | INCOMPATIBLE with primary cell/value target; separate row task only |

CDC's 1000-row default calibration in official code yields calibration_size=1000/n; blindly applying it to 1000-row Hospital is invalid. A dirty-history model may be a legitimate new robust variant, but is not the same published clean-calibrated guarantee. No partial reimplementation is called CDC.

Auto-Test §6.1 explicitly states Relational-Tables and Spreadsheet-Tables are separate from RT/ST tests. That corrects the hypothesis that the paper simply trains on its test set. We have not independently verified the released corpora, foundation encoders or Tablib overlap. Header+value fingerprints find within-release duplicates and two exact cross-benchmark overlaps; source-table identities are missing. Do not describe this as a clean source-independent holdout.

Cell labels cannot be inferred from Isolation Forest row scores. RT/ST contain no joint rows, entity groups or occurrence counts; CDC, multicolumn dBoost and Raha are incompatible with fabricated relational RT/ST tables. A standalone univariate configuration would require its own separately specified implementation and target, not a claimed full-table run.
