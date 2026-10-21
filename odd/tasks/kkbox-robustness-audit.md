# Phase 6 — Frozen-cohort robustness audit
Objective: audit the consumed retrospective benchmark without changing historical evidence.
Branch: feat/kkbox-robustness-audit; base: da86448eb03b7950b8d6a08ea71dde9a23cd3c10; delivery: exception-ok, no PR; runner: .venv/bin/python -m unittest discover -s tests -v.

## Specs
- S1: “La auditoría de leakage y temporalidad está documentada.” Audit source, historical manifests, partitions and selection chronology; distinguish PASS/LIMITATION/BLOCKER/NOT VERIFIED.
- S2: “Las métricas publicadas están verificadas.” Preserve four strategies and all original Phase 5 results; audit formulas, edge cases and tables.
- S3: “No reentrenes, recalibres, ajustes hiperparámetros, cambies características ni vuelvas a seleccionar modelos.” Historical files and consumed marker must remain byte-identical.
- S4: “Un bootstrap pareado correctamente justificado y probado es preferible a varios análisis superficiales.” Fixed subscriber resampling at 5/10/20%, paired strategies, original total ordering, repeated copies, floor capacity, seeded 95% percentile intervals and prefix sensitivity. Conditional descriptive inference only.
- S5: “Los resultados llamativos han sido examinados críticamente.” Frozen-score diagnostics, capacity bands, ties and renewal structure; no unsupported causal/interaction claims.
- S6: “Las limitaciones están clasificadas y documentadas.” Cover data, temporal, evaluation, uncertainty, business and generalization validity.
- S7: “No publiques identificadores, outcomes por usuario, scores individuales, rankings, modelos `.joblib` ni arrays every-K.” Only small global aggregate outputs.
- S8: “No hagas merge a `main`, no crees PR y no empieces la Fase 7.” Commit and push only after tests, audit reproducibility and preservation checks; verify remote SHA and clean tree.

## Tasks
- T1 [S1,S2,S3] inline audit and historical checks; complete, commit 7e501d1b129664c0ec46ba365de96b2735eda7f9; mapping delegated because evidence exceeds bounded inline batch.
- T2 [S4,S5,S7] inline bootstrap, runner, synthetic tests and real aggregates; complete, commit 7e501d1b129664c0ec46ba365de96b2735eda7f9; independent verifier required for outcome/cache alignment (Risk item 6: methodological errors can escape ordinary regression tests).
- T3 [S1,S5,S6,S8] inline documentation, full regression and independent check complete; commit 7e501d1b129664c0ec46ba365de96b2735eda7f9; authorized push/readback is the final delivery operation.

## Log
- L1 (2026-10-21): User request: implement fully “Fase 6 — Reliability, Audit and Limitations”, preserving the original February 2017 cohort, cutoff, seven features, deterministic partitions, frozen LR/HGB, validation selection, original evaluation and post-hoc evidence. User explicitly authorizes branch, tests, docs, commit and push; forbids merge, PR, Phase 7, retraining, recalibration, tuning and reselection. Full original request remains in session transcript; requirements above quote its acceptance strings.
- L2: User: “si trabaja hgasta completar la fase 6 sin preguntar más nada, el repo local esta en main en el commit más reciente , olvidate de engram no lo uses ni intentes usar no lo tengo instalado”. SSH use authorized. Engram tools unavailable; mirror unavailable, local task document authoritative.
- L3: Fetch confirmed origin/main unchanged at base; clean main. Created requested branch from origin/main. Initial sandbox denied .git/FETCH_HEAD; approved git escalation succeeded, no destructive recovery.
- L4: Forecast approximately 700 authored lines including tests/docs; exception-ok single branch, no PR as explicitly requested. Parent writes inline; mapper supplies read-only evidence. Bootstrap planned before inspecting its results: seed 20261021, 2000 replicates, prefix 1000 sensitivity, 5/10/20%, percentile 95% pointwise intervals, three strategy pairs. No significance-driven changes permitted.

- L5: T1 gate accepted real N=174931/P=9527, all 101 public budgets/table, three original outcome reconstructions, original digest, all splits and frozen score/rank alignments. T2 RED missing module then 7 focused tests GREEN; two fixed private runs create-compare exact 9155-byte JSON SHA f1a9d643daf74774916dc28895bf41ff1f054a8138580d7911565f9fd182ddb2. No original non-doc tracked bytes changed (41 files); 43 historical files unchanged during each run.
- L6: Independent verifier PASS S1–S7; 5373 expanded-copy cases and independent paired quantiles, public tamper immutability, four prior CLI output/help differential checks; whole isolated suite 84/84 PASS in 63.915s. Parent spot check focused 7/7 and public audit PASS. Native review globally OFF, unchanged. Risk: item 6, independently checked. Documentation file links 95 PASS. S8 commit/push evidence follows.

- L7: Implementation/evidence commit 7e501d1b129664c0ec46ba365de96b2735eda7f9; 1179 changed lines including the 325-line generated aggregate JSON (854 authored changed lines). One coherent bootstrap/audit delivery with tests and docs kept together; user requested single branch/no PR and allowed scoped commits. Native review remains OFF. Staged scope/credential/aggregate schema checks PASS. Final push and remote-SHA/clean-tree readback belong to the delivery report; no merge or PR.
