# Retention Lab — Project Roadmap

## Project objective

Evaluate how much ML improves identification of future subscription churners
when a business can review only a limited share of eligible subscribers.
The approved scope is a restricted retrospective KKBOX benchmark, not an
operational historical simulation or evidence of churn prevention.

## Implemented stages

| Stage | Delivered outcome |
|---|---|
| 1 — Feasibility | Restricted retrospective protocol: original February 2017 labels, January 31 cutoff, record-based eligibility and explicit availability/label limitations. |
| 2 — EDA | Frozen deterministic user partitions and training-only analysis; executed notebook and aggregate evidence. |
| 3 — Features | Seven cutoff-bounded transaction predictors; conservative ambiguity/missingness handling and isolated final features. |
| 4 — Models | Train-only preprocessing, Logistic Regression and HGB; validation-only selection and committed pre-test freeze. |
| 5 — Evaluation | Original one-shot Random/Rule/HGB evaluation; later descriptive LR addition from its original frozen ranking, published separately. |
| 6 — Robustness | Post-hoc integrity/statistical audit, paired fixed-ranking bootstrap and classified limitations; no retraining or new temporal validation. |
| 7 — Interactive demo | Interactive demo implemented and locally verified; Netlify deployment pending. |
| 8 — Public portfolio | Public presentation and documentation consolidated; final live-demo presentation remains pending. |

Phases 1–6 are complete within their restricted scope. Phase 7 is not fully
complete until deployment and live verification. Phase 8 is in progress, not DONE.

## Technical deliverables

- [Python source](src/retention_lab/), [CLI scripts](scripts/),
  [tests](tests/) and [executed notebook](notebooks/01_eda.ipynb).
- [Methodology](docs/methodology.md), [features](docs/features.md),
  [models](docs/models.md) and [original evaluation protocol](docs/evaluation_history.md).
- [Results](docs/results.md), [robustness](docs/robustness.md),
  [limitations](docs/limitations.md) and [data attribution](docs/data_attribution.md).
- [Static React explorer](web/README.md), backed only by validated public
  aggregates; separate Python and npm dependency contracts.

## Current status

The four-strategy comparison and web implementation are integrated in `main`.
At 10% capacity HGB identifies 62.64% of observed churners, versus 61.35% for LR,
55.91% for the rule and 10.00% expected for random selection. Scientific details
and uncertainty belong in the linked reports, not a task-execution diary.

**Ready for Netlify deployment — live verification pending.** No deployment or
public application URL is claimed.

## Remaining release work

- Separately authorize and perform Netlify deployment, then verify the live
  assets, exact metrics, documentation links, keyboard and responsive behavior.
- Add the real live URL to the README and GitHub homepage after verification.
- Complete portfolio presentation with the deployed demo and final human review.

## Scope and limitations

Final outcomes are consumed; release work does not reopen training, selection,
rankings or bootstrap. Preserve the original three-strategy evaluation and the
post-hoc LR/statistical chronology. There is no temporal external validation,
causal intervention evidence, production scoring, backend or automated campaign.
Dataset and aggregate-publication conditions remain in the attribution document.
