# Four frozen churn ranking strategies

How much observed churn can a subscription team identify when it can contact
only a fixed share of subscribers? The comparison concerns prioritization,
not the causal effect of contacting them.

The four strategies are **Random expected**, **Business Rule**, **Logistic
Regression (LR)** and **HistGradientBoostingClassifier (HGB)**. These are four
curves from three families: random selection, a business rule and ML. The plot
and tables use the shorter label HistGradientBoosting for HGB.

**Original evaluation:** HGB was selected using validation only, committed before
final outcome access, and evaluated once with Random and Business Rule.
**Subsequent extension:** Logistic Regression is incorporated descriptively using
its original pre-test frozen ranking. HGB remains the selected model. This is
not independent confirmatory evidence and cannot justify model reselection.

> Post-hoc descriptive extension using the previously frozen Logistic Regression ranking.

## Same population and definitions

All four policies refer to the same **174,931** eligible final subscribers and
**9,527** observed churners, with feature cutoff **2017-01-31**. Unchanged:
partitions, seven predictors, keys, scores, ties and business rule (auto-renew off
first). `K = floor(N * percentage / 100)`; actual capacities are
4.999686%, 9.999943% and 19.999886% for K=8,746 / 17,493 / 34,986.
Recall=TP/P; Precision=TP/K; Lift=Precision/(P/N).
Random expected is uniform-selection expectation, not a measured permutation:
E[TP]=KP/N, expected recall=K/N, precision=P/N and lift=1 for K>0.
Its fractional captured counts are expectations. Display rounding is never used
as input. Undefined ratios at K=0 or P=0 remain null in JSON.

## Capacity tables

| Strategy | Capacity | Subscribers contacted | Churners identified | Recall@K | Precision@K | Lift@K |
|---|---:|---:|---:|---:|---:|---:|
| Random expected | 5% | 8,746 | 476.32 expected | 5.00% | 5.45% | 1.000 |
| Business Rule | 5% | 8,746 | 2664 | 27.96% | 30.46% | 5.593 |
| Logistic Regression (post-hoc) | 5% | 8,746 | 3876 | 40.68% | 44.32% | 8.137 |
| HistGradientBoosting | 5% | 8,746 | 3993 | 41.91% | 45.66% | 8.383 |
| Random expected | 10% | 17,493 | 952.69 expected | 10.00% | 5.45% | 1.000 |
| Business Rule | 10% | 17,493 | 5327 | 55.91% | 30.45% | 5.592 |
| Logistic Regression (post-hoc) | 10% | 17,493 | 5845 | 61.35% | 33.41% | 6.135 |
| HistGradientBoosting | 10% | 17,493 | 5968 | 62.64% | 34.12% | 6.264 |
| Random expected | 20% | 34,986 | 1905.39 expected | 20.00% | 5.45% | 1.000 |
| Business Rule | 20% | 34,986 | 6612 | 69.40% | 18.90% | 3.470 |
| Logistic Regression (post-hoc) | 20% | 34,986 | 6793 | 71.30% | 19.42% | 3.565 |
| HistGradientBoosting | 20% | 34,986 | 7410 | 77.78% | 21.18% | 3.889 |

Recall differences in percentage points (not relative percentages).

| Capacity | Logistic vs Rule | HGB vs Rule | HGB vs Logistic |
|---|---:|---:|---:|
| 5% | +12.72 pp | +13.95 pp | +1.23 pp |
| 10% | +5.44 pp | +6.73 pp | +1.29 pp |
| 20% | +1.90 pp | +8.38 pp | +6.48 pp |

All five requested pairwise recall differences, including each ML strategy vs
Random expected, are recorded unrounded in the
[versioned JSON](../artifacts/capacity_comparison_v2.json). Only integer-percentage
budgets are exported, not private every-K arrays. The plot renders real every-K
empirical step curves without smoothing, with 5/10/20 markers and exact endpoints;
the dashed gray curve is theoretical. Colors: rule blue, LR green, HGB orange.

## What complexity adds

At the same 5/10/20% budgets, HGB identifies **117 / 123 / 617** additional observed
churners compared with LR: **1.23 / 1.29 / 6.48 recall percentage points**.
The difference is modest at 5/10%, larger at 20% in this cohort. That descriptive
trade-off must be weighed against LR's simpler linear interpretation; it does
not establish statistical significance, operational value or a new winner.
HGB's selected status comes from the pre-test validation decision, not this table.

## Main visualization

![Churn Captured vs. Outreach Capacity](../artifacts/capacity_comparison_v2.png)

## Selection, freeze and post-hoc chronology

Both LR and HGB were trained on the same seven approved features. The
predeclared validation criterion chose HGB only if Recall@10% improved by at
least one percentage point, without a decrease at 5% or 20%. HGB satisfied it;
that decision was frozen before the first final-label access. The original
final evaluation compared Random, Business Rule and HGB. The later LR addition
uses its pre-test frozen ranking, with no retraining or reselection from final
results.

### Historical identity and outcome reuse

Historical chain: original LR `471525b34afdef2783350a734c4c2cfdd8366749` →
HGB freeze `7f21d9bb615ca5834e92fdc3fdf8f0928a62b7e8` →
original evaluator `ec3e58ebf8f0312ab353ab1f854ba058d7c9d669`.
The original LR manifest/model/ranking hashes were already recorded in the first
commit's progress log. All original file fingerprints are reverified, the
committed freeze binds the original LR manifest, and the evaluation manifest
binds the consumed marker and original results/counts/PNG. Both frozen baseline
orders/scores and all keys match exactly. No original artifact is overwritten.

The private every-K capture arrays already contain outcome information. Taking
their adjacent differences and inverting the frozen permutations reconstructs
outcomes **in memory**, without a raw CSV read. Independent inversions from all
three original orders agree and reproduce the original canonical key/outcome
digest. Recomputed three-policy results equal the entire original JSON exactly
before LR metrics are added. No model is loaded, fitted or scored, no winner is
reselected, no original evaluator or original CSV is called. This is controlled
post-hoc reuse, **not a first or second independent test access**.

Run `.venv/bin/python scripts/extend_kkbox_comparison.py --help` for explicit
private input directories and aggregate output destination. The CLI refuses
changed historical identity or conflicting output bytes. Reproducibility assumes
the preserved private evidence and pinned same-platform environment; Git/hashes
are local integrity evidence, not trusted third-party timestamps. Historical
training/selection source bytes stay unchanged, so existing CLI behavior is not
modified. Synthetic tests do not constitute a repeat real experiment.

## Publication and limitations

See [dataset attribution and conditions review](data_attribution.md). The owner
authorized only own code/methodology/global metrics/aggregate visualization,
subject to applicable terms. No express derivative-data permission is asserted.
The original three-policy JSON, PNG, manifests, models, keys, rankings, scores,
consumed marker, every-K arrays and all original CSVs remain private/unchanged.
Public additions are the v2 sampled JSON, table and PNG, code/tests and docs.

Limits: one cohort; retrospective evaluation; no demonstrated temporal
out-of-cohort generalization; no causal evidence, prevented churn or revenue/ROI
claim; post-hoc reuse of already-observed final outcomes. Source arrival times,
label adjudication, history truncation, eligibility coverage and cross-machine
image identity remain limited as documented. No uncertainty interval or
statistical significance claim was added by the Phase 5 comparison. The later
Phase 6 conditional uncertainty audit is reported separately below.

## Reproduction and evidence

- [Public aggregate JSON](../artifacts/capacity_comparison_v2.json) and
  [summary table](../artifacts/capacity_comparison_v2.md): readable without private data.
- [Model guide](models.md#authorized-second-and-final-candidate-2026-10-20) and
  [pre-test freeze snapshot](../artifacts/model_freeze.json): validation decision
  and historical configuration. The snapshot's unopened-test/publication fields
  describe the freeze date, not the current release status.
- [Original LR development diagnostics](../artifacts/model_validation.json):
  train/validation only, not current model selection or final results.
- [README reproduction guidance](../README.md#reproduce-the-descriptive-extension-no-raw-csv-access)
  and [environment](methodology.md#reproduce): procedures only; no pipeline was
  rerun for this documentation maintenance.
- [Archived original evaluation protocol](evaluation_history.md): complete
  original one-shot procedure and then-applicable publication restrictions.
- [Progress log](../PROGRESS.md): dated execution and verification evidence.

## Phase 6 — Subsequent statistical audit

The [robustness report](robustness.md) and [classified limitations](limitations.md)
add a descriptive paired subscriber bootstrap using the already-consumed cache.
They are neither a new independent test nor a model-selection step. Original
Phase 5 point metrics, the four strategies, v1 evaluation and v2 LR post-hoc
extension above remain unchanged. No model was refitted, recalibrated or rescored.

At 5/10/20% capacity, HGB−LR Recall differences are respectively 1.23/1.29/6.48
percentage points; their conditional 95% pointwise percentile intervals are
[0.73, 1.63], [0.89, 1.72] and [5.94, 7.09] pp. HGB−Rule differences are
13.95/6.73/8.38 pp, with intervals [12.98, 14.85], [5.91, 7.50] and
[7.78, 9.08] pp. These describe hypothetical iid subscriber resampling within
this restricted cohort conditional on frozen models and tie orders—not temporal
transferability, causal benefit or a second confirmatory evaluation.

See the [small aggregate audit JSON](../artifacts/robustness_v1.json) for all
three paired comparisons, marginal Recall intervals, fixed seed/configuration,
Monte Carlo prefix sensitivity and newly computed descriptive final-score
AP/ROC-AUC. These diagnostics are distinct from the original development
metrics. They do not replace any original point estimate or reopen selection.
