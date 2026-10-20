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
