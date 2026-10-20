# Four frozen churn ranking strategies

**Original evaluation:** HGB was selected using validation only, committed before
final outcome access, and evaluated once with Random and Business Rule.
**Subsequent extension:** Logistic Regression is incorporated descriptively using
its original pre-test frozen ranking. HGB remains the selected model. This is
not independent confirmatory evidence and cannot justify model reselection.

> Post-hoc descriptive extension using the previously frozen Logistic Regression ranking.

![Churn Captured vs. Outreach Capacity](../artifacts/capacity_comparison_v2.png)

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

## Audit and outcome reuse

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
statistical significance claim is added. Phase 6 has not started.

## Historical original evaluation protocol

The following records the original three-strategy protocol and then-applicable
publication hold. Those files and their private metadata are preserved verbatim;
the limited publication policy above supersedes the historical local hold only.

# Capacity evaluation protocol and publication hold

The question is how many observed future churners are identified when contact
capacity is limited. This is a retrospective February-2017 cohort comparison,
not an operational deployment simulation or an estimate of churn prevented.

Model selection uses validation **only** and is committed before final outcomes.
See [the model guide](models.md#authorized-second-and-final-candidate-2026-10-20).
The authorized final evaluation is one pass over the three frozen policies;
no final-based retraining, feature/parameter/tie changes or model reselection.

## Definitions fixed before results

For N users, P observed positives, contact percentage c and TP captured positives:

- `K = floor(N*c/100)`; actual contact capacity is `K/N`.
- `Recall@K = TP/P` if P>0, otherwise JSON null.
- `Precision@K = TP/K` if K>0, otherwise null.
- `Lift@K = Precision@K/(P/N)` if K>0 and P>0, otherwise null.
- At K=0, TP=0 and recall=0 only if P>0.
- At K=N with P>0, recall=1 and lift=1. Empty populations are rejected.

Rankings must be complete permutations of the exact unique frozen final keys.
Scores tie via the already frozen purpose-specific hashes, never outcome values.
Uniform random expectation has E[TP]=K*P/N and expected recall K/N when defined;
this is distinct from the measured deterministic random permutation. All recall
differences are signed **percentage points**, `100*(ML-reference)`.

## Privacy and current publication boundary

No new empirical result is published here. New validation metrics, final tables,
curve JSON and plot must remain in ignored owner-only private storage until
publication rights are established. The [official rules](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules)
permit educational/research use subject to acceptance but restrict data sharing;
no explicit clearance for this project's derived aggregates was established.
A private result must not be mistaken for a public release or a DONE publication
gate. Exact execution status and remaining work are in [progress](../PROGRESS.md).

## Interpretation and limits

A higher Recall@10% means that reviewing the same limited number of subscribers
includes more eventual churners in this historical cohort. It says nothing about
whether a contact changes their outcome. No prevented churn, saved revenue or ROI
is estimated. Limits include one cohort, no cross-month temporal validation,
unverified historical arrival times and label adjudication, left-truncated
history, record-based eligibility, and no intervention/causal evidence.

## Private one-shot execution

After the explicit freeze commit has been verified, the authorized command is:

```sh
.venv/bin/python scripts/evaluate_kkbox.py \
  --freeze-commit 7f21d9bb615ca5834e92fdc3fdf8f0928a62b7e8 \
  --verify-real-population
```

Do not run this as a development experiment. `--labels` defaults to original
`data/raw/train.csv`; `--frozen-dir`, `--feature-dir`, `--eda-dir` and
`--output-dir` select explicit nonoverlapping private locations. No v2 source.
The gate verifies committed anchor/source bytes, model/provenance/environment,
recomputed predictions, exact final keys and all policy permutations before
outcome access. Then an exclusive `evaluation_started.json` record is flushed
and fsynced in the freeze directory **before** opening outcomes. Any subsequent
failure leaves the attempt consumed; there is no silent label-read retry.

CSV parsing transports all fields, but the evaluator converts and hashes outcome
values only after final-key membership. All source identifiers are checked against
the frozen identifier-only fingerprint; final labels must join exactly to keys.
Nonfinal outcome values are not validated, interpreted or hashed. This is a
data-flow guarantee, not physical selective disk access or OS isolation.

Default private output is `data/processed/kkbox-evaluation-v1/` (0700):
`results.json` has 101 measured budgets and a 5/10/20 table;
`capacity_curve.png` shows the full empirical step curves at **every integer K**
and theoretical random expectation; `curve_counts.npz` retains every-K counts
for reproduction without reopening labels. **Never publish the every-K arrays:**
differencing them can recover ordered outcomes. The completion manifest hashes
all outputs and binds the start record, freeze commit/manifest, evaluator code
and selected-label provenance. There are no exported subscriber IDs.

An identical later CLI call verifies and reads the completed cache without
opening or even requiring raw labels. A different destination, changed identity,
partial run or corrupt output is refused. This is not permission to repeat the
final experiment. Plot reproduction uses the cached counts with `render_curve`;
no training or label source is needed. A writable external `MPLCONFIGDIR` avoids
sandbox home-cache warnings. Package deprecation warnings are not convergence
failures and do not justify changing the frozen numerical environment.

## Observed execution status

**Private evaluation complete; Phase5 publication BLOCKED, not DONE.** Freeze
commit `7f21d9bb615ca5834e92fdc3fdf8f0928a62b7e8` predates outcome opening.
All three policies cover the same 174,931 final keys. One real evaluation ran;
no selection/training/policy changes followed. All new empirical numbers and
figures remain private. The PNG was reproduced byte-for-byte from cached counts;
a verified cache readback succeeded without any available raw-label file.
Neither operation constitutes a second final evaluation.

Private manifest/model/output hashes, run chronology, actually executed tests
and publication blocker are recorded in `PROGRESS.md`. The developer separately authorized committing/pushing the current evaluator
code, tests and documentation, without the private empirical outputs. If clearance is obtained, export only
approved sampled aggregates and the PNG from this frozen cache; never export
subscriber records, scores, model pickle, every-K counts or the raw outcomes.
Do not rerun the final experiment to prepare publication.

For an interview, explain the decision chain: compare the fixed LR and bounded
HGB on validation, choose using the predeclared limited-capacity criterion, commit
that choice, and measure once on untouched final outcomes. Better Recall@10%
means more observed churners included within the same contact count, not more
customers retained. The private table quantifies that difference; no causal
or cross-month generalization claim follows.
