# Four frozen strategies — post-hoc descriptive extension
Branch: `feat/kkbox-model-baselines`; delivery: one explicitly requested completion commit, no PR/merge; estimated 650 authored lines plus generated aggregates. Runner: `.venv/bin/python -m unittest discover -s tests -v`.
Engram unavailable: full persistent mirror pending. Existing implementation and private evidence remain immutable.

## Specs

- S1: "No vuelvas a entrenar Logistic Regression." / "No vuelvas a entrenar HGB." / "No repitas la selección de modelo." HGB remains selected on validation.
- S2: "Si el ranking original de Logistic Regression no puede verificarse, detén la ampliación final." Verify original model/manifest/rankings and historical commit relationships before deriving metrics.
- S3: "No accedas de nuevo a los CSV originales." Reconstruct outcomes only in memory from verified private cached counts, invert frozen orders, require identical outcomes from all three orders and the original selected-label digest.
- S4: "174.931 usuarios." / "9.527 churners." / "K = floor(N × porcentaje / 100)". Preserve keys, feature schema, orders/ties, policies and original three-policy values.
- S5: "Post-hoc descriptive extension using the previously frozen Logistic Regression ranking." Separate v2 result; retain all v1 files and consumed marker.
- S6: Four strategies at 5/10/20: Recall@K, Precision@K, Lift@K, captured, selected, effective capacity; five requested pairwise recall differences in percentage points. Random is expected, not a realized draw.
- S7: "Churn Captured vs. Outreach Capacity"; "Subscribers selected (%)"; "Observed churners identified (Recall, %)". Gray dashed expected random, blue business, green LR (post-hoc), orange HGB; empirical unsmoothed steps, endpoints and 5/10/20 markers.
- S8: Publish only sampled aggregates and visualization; no IDs, labels, scores, models, rankings, private runs or every-K arrays. Attribute WSDM 2018 KKBOX/Kaggle, independent educational project, original files acquired under official rules, no inferred express derivative permission.
- S9: Preserve original evaluation and document post-hoc reuse, single-cohort retrospective limitations, no temporal/causal/prevented-churn claims. Update README, PROGRESS, ROADMAP, models/results and attribution.
- S10: "feat(results): compare four frozen churn ranking strategies"; push only after checks; verify remote HEAD and clean tree. "No hagas merge." / "No abras PR." / "No hagas force-push." / "No comiences la Fase 6."

## Tasks

- T1 (S1–S5) inline: audit historical artifacts and implement separate cache-only extension; verified; no writer trigger (one dependent behavior).
- T2 (S6–S9) inline: synthetic tests, versioned aggregate exports/plot and documentation; verified.
- T3 (S1–S10) independent verification PASS; parent staged publication/commit/push authorized after checks. Completion commit: `feat(results): compare four frozen churn ranking strategies` (self; SHA in final delivery report). Risk: item 2 (privacy boundary for derived outcomes/public exports). One independent verifier required.

## Log

- L1 — 2026-10-20 authorized outcome: "Objetivo final: una comparación visual y cuantitativa de Random, Business Rule, Logistic Regression y HistGradientBoosting que sea reproducible, comprensible y metodológicamente honesta, sin rehacer el entrenamiento ni ocultar que el test final ya se utilizó." Full detailed user request retained in conversation; specs above preserve acceptance constraints.
- L2 — Clean branch HEAD/local remote ec3e58ebf8f0312ab353ab1f854ba058d7c9d669; all three historical references are ancestors in order; GitHub reports no existing PR for branch. Initial sandbox DNS failed, elevated authorized read succeeded.
- L3 — Independent read-only audit verified original LR model/manifest/ranking, all freeze/evaluation hashes, same 174931 unique keys/seven features. Counts inversion from three orders matches original selected-label hash. No CSV/training/scoring/selection/evaluator executed.
- L4 — Rules reviewed from indexed official page on 2026-10-20: section 7 restricts competition-data redistribution; section 8 permits own public code. No express prohibition specific to aggregate metrics/plots found. Apply owner's conditional authorization; do not assert express derivative license. Original historical holds remain historical evidence, not rewritten.
- L5 — Source-mutating normalizers: none configured/needed; separate new files only. Existing training/selection/evaluation implementation must stay byte-identical. RDD globally disabled, unchanged. Forecast exceeds 400 lines; one coherent cache-only audit/export behavior with its tests/docs, explicit user single-commit delivery takes precedence over PR chaining. No PR to create.

- L6 — Six focused tests GREEN, after five missing-module RED cases. Real cache-only CLI succeeded twice byte-identically, second run guarded against raw CSV, fit/score/selection/original evaluator. No real training/scoring/selection done. Original entire results JSON rebuilt equivalently in memory only; every original manifest/output/marker remains unchanged.
- L7 — Public candidate scan passed for all 13 files against all 174931 final identifiers, home paths and credential markers; private data/model/rank/cache outputs ignored, only placeholders tracked. New public JSON has 101 sampled budgets (not every K). Parent visually inspected PNG. Independent review: no blockers; all101 budgets/formulas/five deltas checked, eight historical CLI help probes equivalent, all existing source/script/test bytes identical to baseline.
- L8 — Independent fresh full-suite setup initially omitted .gitignore:76/77 passed; omitted-file module rerun4/4 and focused6/6 passed after correcting scratch setup. A corrected complete suite is running to satisfy final full-run closure. This was a verifier-copy error, not a source/test failure.

- L9 — Corrected independent full scratch suite77/77 PASS in63.360s; parent final focused6/6 PASS. No verifier blockers; no source changes after review. Normalization not applicable, diff whitespace clean. Risk item2 independently verified; RDD remains globally off.
- L10 — Local analytical/publication acceptance complete. Completion commit uses exact requested message and includes code/tests/docs/aggregates as one behavior. Commit/push/remote SHA and clean-worktree evidence reported after commit; no PR/merge/Phase6. Rollback surface: new posthoc module/CLI/tests/v2 artifacts/attribution/task and current documentation additions only, never original private evidence. No old command shares changed source, so old CLI differential results are unchanged. Persistent mirror/session summary pending solely because Engram tools are absent.
