# Phase 6 — Reliability and frozen-cohort audit

The historical comparison is internally consistent. A paired subscriber bootstrap
supports positive descriptive Recall@K differences for all three model/rule pairs
at 5%, 10% and 20%, **conditional on this cohort and frozen rankings**. It does
not validate another month, historical deployment or retention impact. HGB stays
selected; neither the audit nor these intervals reopen model selection.

## Reproduce without repeating the experiment

```sh
# Public metrics only; no private data needed:
.venv/bin/python scripts/audit_kkbox_robustness.py
# Requires the intact private EDA/features/models/selection/evaluation caches:
.venv/bin/python scripts/audit_kkbox_robustness.py --private
.venv/bin/python -m unittest discover -s tests -v
```

The private command has one fixed configuration, no training/evaluation path and
no raw-input argument. It reads the consumed cache through the existing
`posthoc.extend_from_cache` integrity gate. Three original cumulative-count
inversions must agree, and the recovered sorted-key/outcome digest must match
the original evaluation manifest. LR alignment is additionally checked. Keys,
scores and rankings are verified against historical hashes and the purpose-hash
total order. `train.load_inputs` verifies all assignments, split digests, schemas,
coverage and permitted label alignment, without fitting anything.

Output: [robustness_v1.json](../artifacts/robustness_v1.json). Existing output must
match exactly; conflicts fail rather than overwrite. No final-label source,
serialized model or original evaluator is opened/executed. Importing the existing
pure result builder through the post-hoc verifier is not invoking `evaluate_once`.

## Integrity and leakage matrix

PASS means checked evidence, not an assertion of source authenticity. LIMITATION
means a known boundary compatible with the restricted contract. NOT VERIFIED
means missing evidence. No invalidating BLOCKER was observed.

| Check | Verdict | Evidence and exact scope |
|---|---|---|
| Cutoff and all seven features | PASS | `data.py` filters `transaction_date > 20170131` before daily/history aggregation; `features.py` whitelist and manifest; synthetic future-event, ambiguity and deduplication tests. No cold rebuild of original CSVs in Phase 6. |
| Eligibility | PASS | Source uses unambiguous latest expiry/cancel/renewal state, February expiry and cancel=0; frozen assignment/population manifests verified. 874,581 candidates, 874,580 labeled; one excluded. This verifies the implemented contract, not operational observability. |
| Future recorded expiry | LIMITATION | February expiry can be recorded in a January transaction; not itself future-event leakage. Exact event semantics and arrival times remain unproved. |
| Churn/maturity | LIMITATION | Supplied February `is_churn` under 30-day non-renewal concept; late-February follow-up reaches March 30. Retrospective fitting only after maturity, conservatively March 31 plus unknown processing lag. |
| Arrival/release times; independent label adjudication | NOT VERIFIED | No ingestion timestamps, independently reconstructed target or source release proof. Cannot claim a February 1/March 1 deployment simulation. |
| Predictor exclusion | PASS | Exact seven-column schema; IDs, labels, split hashes and holdout metadata are separate; guard rejects extras. No final-outcome field in feature tables. |
| Partitions and alignment | PASS | Real `load_inputs(..., verify_real=True)` checks every salted SHA-256 assignment and sorted unique key, full manifest coverage and feature/allowed-label rows. Train 523,998; validation 175,651; final 174,931. |
| Training-only learning | PASS | Source and existing perturbation/guarded-I/O tests: LR median/imputer/scaler/classifier fit training only; HGB training only, native missing routing. Historical model bytes unchanged. This is source/test/provenance evidence, not a new training execution. |
| Validation-only selection | PASS | Historical LR → HGB freeze → evaluation ancestry and anchors verified; predeclared validation Recall@10% criterion, 5/20% guards. Frozen HGB predates consumed evaluation. |
| LR addition | PASS | Original LR model and rankings match pre-test manifest; separate v2 is explicitly post-hoc. It is not independent confirmatory evidence. |
| Earlier outcome exposure | LIMITATION | Phase 1 global-label diagnostics are recorded in the historical progress log; they cannot be undone. Subsequent feature/development isolation is source/test verified; no absolute claim that nobody ever saw final-associated outcomes. |
| Final cache identity and public metrics | PASS | Three outcome inversions, canonical digest, manifests and consumed marker; original v1 rebuilt in memory; entire public v2 JSON and table match. All 101 budgets checked independently for floor rounding/formulas/deltas/monotonicity. |
| Original experiment preservation | PASS | 43 historical/private/public files hashed before/after each real audit; frozen source hashes accepted. No refitting, rescoring, raw CSV reopening or consumed-marker removal. |
| Official source authenticity | NOT VERIFIED | Local checksums prove local identity, not official download authenticity or external timestamps. |
| Temporal transfer and causal benefit | NOT VERIFIED | No other month or intervention outcome exists. These are explicitly excluded claims, not failed requirements of this restricted benchmark. |

## Metrics and plot audit

For N users, P positives, TP selected positives, use `K=floor(N*p/100)`,
Recall=TP/P, Precision=TP/K, Lift=Precision/(P/N), prevalence=P/N. Differences
are `100*(Recall_A-Recall_B)` **percentage points**, not relative percent.
Existing tests cover K=0/N, zero positives, invalid budgets, incomplete/duplicate
permutations and invalid outcomes. Undefined denominators are null, not zero.
At K=0 with P>0, Recall=0 while Precision/Lift are undefined.

AP is noninterpolated average precision: the sum of precision times increases
in recall at distinct score thresholds. ROC-AUC is the positive/negative
concordance probability with half credit for tied scores. AP is **not**
trapezoidal PR-AUC. A new tied-score hand example verifies AP=5/6 and AUC=.875.
Diagnostics use original scores, while capacity metrics use the frozen total
orders, including deterministic hash ties. These are different tie conventions
for different quantities, not contradictory evaluations.

The unchanged PNG uses the verified every-K empirical steps and expected-random
line (not a fitted smooth curve); the public JSON samples 101 budgets. Visual
inspection checks four curves, markers and labels. Existing plot tests check
rendering/reproducibility; the image itself is not a machine-readable metric
source. Original points and all four strategies remain unchanged.

## Fixed bootstrap protocol

- Prespecified before computing new results: seed **20261021**, NumPy default
  generator (PCG64), **2,000** replicates, prefix **1,000**, capacities **5/10/20%**.
- Draw N subscriber indices uniformly with replacement. A single integer
  multiplicity vector is shared by HGB, LR and rule in each replicate; outcomes
  remain attached to those same indices. Do not resample curve points or policies
  independently. Do not stratify: prevalence can vary across replicates.
- Sort repeated copies by the **original frozen total order** per strategy
  (score descending then original purpose-specific hash/ID). Copies of one user
  are adjacent and identical. Their within-user order cannot change captured
  positives. Count only the required copies when a multiplicity crosses K.
- Keep N and `K=floor(N*p/100)` identical across strategies and replicates.
  Denominator P is the positive count **in that replicate**, not original P.
- Report empirical 2.5/97.5 quantiles using NumPy `method='linear'`. Compute
  paired differences inside each replicate, then their quantiles—not subtraction
  of two marginal intervals. Original point estimates remain the estimates.
- Zero-positive replicates are undefined, excluded and counted; all-zero source
  outcomes refuse analysis. Here **0/2,000** replicates were undefined.
- Percentile intervals keep a modest implementation and avoid a large jackknife
  for discontinuous top-K statistics. They are approximate, not exact-coverage
  guarantees; no BCa, simultaneous bands, p-values or multiplicity correction.
  See [SciPy paired/percentile definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
  and [NumPy quantiles](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html).

Assume exchangeable, independent subscribers from a population resembling this
restricted cohort, conditional on the fitted models and deterministic tie policy.
Shared plans, campaigns or time effects may violate independence. The observed
finite cohort itself has exact point metrics; bootstrap uncertainty refers to
hypothetical subscriber resampling, not uncertainty in its recorded counts.
It excludes training/model-selection variability, alternate tie seeds, target
error, temporal shift and cohort selection bias. The already-consumed final set
and post-hoc LR comparison prohibit confirmatory/generalization claims.

## Results: paired Recall differences

95% pointwise percentile intervals; all values below are **percentage points**.

| Capacity | HGB − LR | HGB − Rule | LR − Rule |
|---|---:|---:|---:|
| 5% | 1.23 [0.73, 1.63] | 13.95 [12.98, 14.85] | 12.72 [11.76, 13.65] |
| 10% | 1.29 [0.89, 1.72] | 6.73 [5.91, 7.50] | 5.44 [4.65, 6.17] |
| 20% | 6.48 [5.94, 7.09] | 8.38 [7.78, 9.08] | 1.90 [1.40, 2.42] |

| Capacity | HGB Recall, % [95% interval] | LR Recall, % [95% interval] | Rule Recall, % [95% interval] |
|---|---:|---:|---:|
| 5% | 41.91 [41.07, 42.72] | 40.68 [39.85, 41.54] | 27.96 [27.13, 28.75] |
| 10% | 62.64 [61.77, 63.56] | 61.35 [60.47, 62.29] | 55.91 [54.97, 56.99] |
| 20% | 77.78 [76.96, 78.65] | 71.30 [70.38, 72.20] | 69.40 [68.46, 70.29] |

Across all paired differences, extending 1,000 to 2,000 replicates moves an
interval endpoint by at most **0.0715 pp**; for marginal Recall intervals the
maximum is **0.0605 pp**. All paired intervals remain positive in both prefixes.
This is a limited Monte Carlo sensitivity check on one seed, not proof of
asymptotic coverage or independent replication. Repeating the identical fixed
configuration must reproduce the entire aggregate artifact byte-for-byte.

## Frozen-score diagnostics and alternative explanations

These are **new descriptive final-score diagnostics**, not replacements for the
original training/validation diagnostics or new model selection evidence.

| Strategy | Average precision | ROC-AUC | Brier score | Unique scores |
|---|---:|---:|---:|---:|
| HGB | 0.396124 | 0.872788 | 0.039800 | 10,659 |
| LR | 0.341869 | 0.818756 | 0.041404 | 27,000 |
| Business Rule | 0.219303 | 0.788627 | not a probability | 2 |

HGB's stronger global ranking does not imply the same margin at each budget.
From 5→10%, HGB captures 1,975 additional positives versus LR's 1,969; from
10→20%, it captures 1,442 versus 948. Thus 494 of the 617 extra HGB detections
at 20% arise in that latter band. This locates the advantage; it does not identify
which feature interactions caused it. Training/validation diagnostics remain
historical development results and are not pooled with this final population.

Overall prevalence is 9,527/174,931 = **5.4461%**. The frozen renewal-off group
contains 21,006 users (**12.0082%** of the cohort), 6,344 positives, prevalence
**30.2009%**; renewal-on contains 153,925 users, 3,183 positives, prevalence
**2.0679%**. The simple rule orders the entire first group ahead of the second,
using hash ties within each. This directly explains its strong concentration and
its slope change near 12% capacity. It is a cohort association, not evidence
that disabling renewal causes churn or that enabling it prevents churn.

HGB/LR also have many tied scores. Existing total orders make observed metrics
reproducible, but conditional bootstrap does not quantify sensitivity to alternate
hash tie-breaking. Truncated observed history is not true tenure; record-based
February-expiry eligibility enriches a specific subset. These features of cohort
construction and target definition are alternative explanations for unusually
strong ranking—not evidence for broad population performance.

Brier scores are descriptive proper-score summaries combining calibration and
discrimination; smaller HGB Brier alone does **not** establish calibration.
No recalibration, calibration optimization, SHAP, feature search or tuning was
performed. Additional calibration bins would add scope without changing this
limited-capacity ranking interpretation, so they are not published.

## Publication and validity boundary

The new JSON is a small set of whole-cohort intervals, three large capacity
bands, global diagnostics and two large renewal groups (smallest N=21,006).
It contains no identifiers, per-user labels/scores, rankings, replicate arrays,
models or every-K counts. Bounds aggregate 2,000 resamples and cannot be differenced
into an ordered outcome sequence. This is a contextual disclosure review, not a
formal differential-privacy guarantee; do not extend this release to small groups
or arbitrarily many slices. Existing owner authorization and
[data-attribution policy](data_attribution.md) apply; no express derivative-data
license or fresh legal clearance is claimed.

See [classified limitations](limitations.md) and [original results](results.md).
