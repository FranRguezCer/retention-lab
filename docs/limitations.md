# Limitations and threats to validity

These limits bound a **restricted retrospective February 2017 KKBOX benchmark**.
No invalidating leakage was found in the audited implementation/evidence chain.
That is not proof of official source authenticity, operational feasibility,
future performance or causal retention. See the [audit matrix](robustness.md).

Severity: **High** prevents a broader claim; **Moderate** can affect estimates
within interpretation; **Low** is a controlled reporting/reproduction limitation.
These are not probabilities of failure, and high severity does not invalidate
the explicitly restricted descriptive question.

| Category / limitation | Possible effect | Available evidence | Severity | Future mitigation |
|---|---|---|---|---|
| Data validity — provenance/authenticity | Local files may differ from authoritative competition release; hashes alone cannot prove origin | Frozen local fingerprints and original-only schema; no independently authenticated download | High for authenticity claims | Authorized download with verifiable release provenance and independent schema reconciliation |
| Data validity — quality/deduplication | Exact textual duplicate collapse can remove indistinguishable genuine events; ambiguous latest states exclude users | Shared deterministic deduplication and daily-agreement logic; synthetic tests and historical quality aggregates | Moderate | Reliable event IDs, payment semantics and independent quality reconciliation |
| Data validity — coverage/history truncation | Observed history is not tenure; counts depend on observation length; supplied labels and expiry-based eligibility select a subset | Seven-feature definitions; original event window and frozen 874,580 labeled cohort, one unlabeled candidate excluded | High for all-subscriber inference | Longer verified history, account inception and population coverage audit |
| Temporal validity — event versus arrival time | Backdated records might not have been available at historical decision time | January 31 event-date filtering verified; no arrival/version timestamp | High for operational backtests | Immutable as-of snapshots with ingestion times |
| Temporal validity — outcome maturity/adjudication | February labels cannot support February 1 or March 1 model deployment; exact boundary errors unknown | Supplied labels, official 30-day concept; follow-up potentially through March 30; release/processing lag unknown | High for deployment claims | Independently regenerate outcomes after complete follow-up and verify release timestamps |
| Temporal validity — one retrospective month | No estimate of performance drift, seasonality or later cohorts | One original February 2017 cohort and cutoff | High for temporal claims | Prespecified multi-month forward validation after label maturity |
| Evaluation validity — user rather than temporal splits | Shared era/process patterns can appear across partitions; no temporal independence | Salted deterministic disjoint partitions and coverage verified | High for temporal claims | Later-cohort external test with locked protocol |
| Evaluation validity — historical exposure | Initial global-label diagnostics cannot be undone, even though later development gates isolate final outcomes | Historical progress record; guarded I/O and poisoning tests; no claim of never-seen labels | Moderate | Fresh independently held test and access-control logging |
| Evaluation validity — selected model and consumed test | HGB selection followed validation; LR was added after final access, so comparisons are descriptive, not a second confirmatory test | Historical pre-test freeze anchors, original consumed marker, unchanged LR ranking | High for confirmatory claims | Pre-register all comparisons and evaluate on new untouched data |
| Statistical uncertainty — conditional iid bootstrap | Misses dependence between users, model-fitting/selection variability, target error, bias and drift | 2,000 paired user resamples, seed 20261021, fixed models/order, prefix sensitivity | Moderate within cohort; High outside it | Cluster-aware sampling with justified clusters, independent cohorts and training uncertainty design |
| Statistical uncertainty — top-K/ties and interval method | Discrete boundaries and fixed hash ties may affect coverage; percentile intervals are approximate and pointwise | Explicit multiplicities/partial boundary, exact floor capacity, unique-score diagnostics; no alternate tie seed study | Moderate | Prespecified tie sensitivity and coverage simulation for the intended population; simultaneous intervals if required |
| Business interpretation — detection is not prevention | No claim of retained customers, contact effectiveness, uplift, revenue or ROI follows | Only observed churn labels and rankings; no intervention assignment/outcomes/costs | High for causal/business-impact claims | Ethical randomized contact experiment with treatment outcomes and costs |
| Generalization — era/company/population | Old KKBOX behavior and selected eligible users may not represent another month, firm or active population | 2017 original-vintage cohort only; no external data | High | Independent current-domain validation with matching decision-time data |
| Publication/reproduction — access and rights | Readers without authorized private data cannot reproduce empirical bootstrap; owner authorization is not a derivative-data license | Public synthetic tests and small aggregates; attribution review, private frozen cache required | Low for code; High for unrestricted redistribution | Authorized source access, maintained terms review and explicitly permitted aggregate release |

## What remains defensible

The frozen strategies can be compared on the **same recorded eligible users** at
fixed capacities. Their historical point metrics are preserved. Paired bootstrap
intervals describe conditional sampling variability under stated assumptions;
they do not repair source uncertainty or turn the consumed test into development
data. No reweighting, tuning, retraining, recalibration or reselection was used
to make the result more favorable.
