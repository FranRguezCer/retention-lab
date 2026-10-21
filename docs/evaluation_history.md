# Evaluation history — archived original three-strategy protocol

> **Historical archive, not current project status or execution instructions.**
> The original protocol below is retained with references updated to public evidence.
> It predates the public four-strategy extension. Its publication hold and
> Phase 5 NOT DONE statements applied at that time, not to the current release.
> See [current results](results.md) and [current publication boundary](data_attribution.md).

The original final test was evaluated once after the HGB freeze. LR was added
later using its pre-existing ranking and private cached evidence. That extension
is descriptive post-hoc reuse, not independent confirmation. The original
consumed marker and private evidence remain preserved. **Do not rerun the
historical command below, reopen labels, retrain or reselect models.**

---

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
gate. Current release status is in the [roadmap](../ROADMAP.md).

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

Historical private fingerprints remain anchored in the commits described in
[current results](results.md#historical-identity-and-outcome-reuse); the original
publication blocker is preserved here. The developer separately authorized committing/pushing the current evaluator
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
