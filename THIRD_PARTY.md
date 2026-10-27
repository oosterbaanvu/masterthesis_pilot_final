# Source attribution and limits

This repository preserves the original dataset audit and adds new research orchestration and adapters. Exact upstream revisions and source licences as found are in `configs/thesis_pilot/sources.json`. Original third-party implementations are fetched into ignored local caches, not vendored here.

- dBoost: Clément Pit-Claudel, Zelda Mariet, Rachael Harding and Samuel Madden; GPLv3. Separate worker/compatibility scripts are labelled GPL-3.0-or-later; the GPL text is retained in `licenses/`. Numeric/text configurations are not separate families.
- LUCARIO: Qin and collaborators, mooselab replication package. No top-level code licence located; no unrestricted reuse permission is invented. The adapter calls the author implementation locally, including full regex inference, and its application parity is tested. No author source or source-value constraint model is redistributed.
- CDC: Sebastian Jäger and Felix Biessmann; original cleaner MIT, conformal-inference Apache-2.0. The actual author implementations run in their supported environment. The reduced supported RF/XT compute budget is disclosed. Source-type experiments are separate adaptations.
- Raha: Mohammad Mahdavi and collaborators, Apache-2.0 author repository. Original learning stages are used with the supported KB-disabled strategy configuration and a metered binary-label oracle; this is not an unqualified full-default/no-label comparison.
- tab_err: Philipp Jung, Sebastian Jäger and collaborators; Apache-2.0. Official 0.2.2 Git source is pinned; placement uses the original hard-window implementations. Operation changes are explicitly logged and independently validated.
- UCI Default of Credit Card Clients: Yeh and Lien; UCI source DOI 10.24432/C55S3H. Bank Marketing: Moro, Cortez and Rita; UCI source DOI 10.24432/C5K306. White Wine Quality: Cortez and collaborators, UCI dataset 186. UCI pages describe CC BY 4.0; cite the original datasets/papers. Full source bytes remain ignored.
- Qwen/Qwen3-0.6B-GGUF: Apache-2.0 per official model card; exact checkpoint SHA and repository revision recorded. llama.cpp MIT; pinned runtime source and actual local execution recorded. Neither weights nor build products are committed.

Publisher-reference benchmark rights and label semantics remain conditional. Generated/statistical findings do not establish independent semantic correctness, customer independence or commercial deployment permission. Auto-Test and ZeroED are investigated sources, not executed full-performance claims.
