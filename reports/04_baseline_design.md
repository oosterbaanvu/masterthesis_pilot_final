# Conventional-control qualification

**Stage C is not passed for a primary empirical comparison.** A programmable control runner and tested numeric/type guards are present, but no credible, source-authoritative extended baseline has been frozen for a primary accepted dataset. Generic missingness alone must not be labelled a mature enterprise baseline.

Proposed A: documented requiredness, exact datatype/format, documented categorical domains, key uniqueness. Proposed B: all A plus independently justified cross-field constraints and training-only statistical envelopes/frequency/length checks. Keep hard validity violations distinct from statistical alerts. Rule authors never receive evaluation references or error coordinates. Freeze rule sources, versions, parameters and exceptions before evaluation.

Hospital: published FD constraints are candidate relation checks, not evidence of which participating cell is corrupt. Repeated provider identifiers reflect multiple measures, so a provider-unique rule would be false. `empty` is a released missing convention, not proof every such cell is required. Zip/phone/provider identifiers remain strings. Hospital score/sample fields contain legitimate textual values. A domain expert/source contract is still needed for cell-specific requiredness and permissible ranges.

Beers: ounces units are indicated by column semantics, but `%` versus fraction ambiguity cannot be fixed from held-out clean values. IBU can legitimately be unavailable. Brewery ID repeats across beers; beer-level keys need separate validation. Brewery↔city/state rules might reflect multi-site entities; candidate FDs are not automatically business truths. No canonical city dictionary is learned from clean values.

Flights: flight ID and source determine the observation context; observations from multiple providers must remain grouped. A consistency violation implicates multiple records, not one known wrong cell. Time zones, dates and date rollover require source specifications. Rayyan: ISSN lexical/check-digit tests may be defensible independently, but missing publication volume/issue and dates are not universally invalid. No US-only postcode rules are applied to multilingual data.

RT/ST: headers and distinct values alone do not supply requiredness, row uniqueness, cross-field contracts, valid code domains or frequencies. Training-only semantic-type/format and length-distribution controls may form a **generic column-control** comparison. That is a narrower claim than value beyond an enterprise's documented business rules. Rules learned from a dirty column must be reported as transductive. No occurrence-weighted profiling is possible.

UCI Credit: documented education/marital/payment codes have observed exceptions; do not relabel all undocumented codes as proven errors. Negative bill balances can be valid. Outcome default is not a DQ label. Bank: `unknown` and `pdays=999` are source conventions; outcome y is excluded. Contract design may use official descriptions plus dirty training data, never final test changes.

Restaurant/Cars: `?` missingness in generated versions can be a secondary ceiling check; class is grouping metadata only. The distinction between 125 scored restaurant changes and 30 class changes must be preserved. Cars numeric formatting has 710 equivalents, not 710 semantic errors. Neither source rescues the required natural-error primary population.

`run_rules` explicitly checks numeric parsing before bounds. Tests include NaN, bad types, invalid codes and missing tokens; a skipped numeric check cannot silently make the baseline weak. No benchmark-specific baseline performance claim is made.
