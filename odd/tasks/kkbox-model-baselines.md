# Phase 4 — Reproducible churn ranking baselines
Implement and freeze Phase 4 only. Branch: `feat/kkbox-model-baselines`; base: `7efdd4fd138005c451d5be5e4840df947be1d7b7`.
Delivery: one requested completion commit and push, no PR/merge; forecast ~900 authored lines. Runner: `.venv/bin/python -m unittest discover -s tests -v`.

## Specs
- S1: "Comprueba que la Fase 3 está marcada como DONE y que su implementación está integrada en `origin/main`." Reuse existing branch explicitly authorized after clean fetch/main/ancestry verification.
- S2: "Selección aleatoria reproducible." "No reutilizar directamente el digest de particionado como ranking si puede evitarse." "Priorizar clientes con renovación automática desactivada." Use distinct purpose-specific hashes; equal random priority and binary business priority, deterministic ties.
- S3: "Utiliza exclusivamente las siete características aprobadas en Fase 3:" `auto_renew`, `observed_history_days`, `january_transactions`, `distinct_transactions`, `latest_plan_days`, `latest_amount`, `auto_on_to_off`. "Todos los parámetros aprendidos durante el preprocesamiento deben ajustarse **exclusivamente con entrenamiento**." "Comprueba la convergencia."
- S4: "Selecciona el candidato final exclusivamente con entrenamiento y validación." "ML no tiene obligación de superar al baseline." One Logistic Regression first; no extensive search or unnecessary alternative.
- S5: "No consultes las etiquetas finales." "No calcules prevalencia del test." "No modifiques las particiones." Final features may be scored; no final label input, hashing or diagnostics.
- S6: "Claves de alineación separadas de las matrices predictivas." "Manifiesto de procedencia y hashes que permita verificar identidad del modelo y de los rankings." Private ignored create-or-compare outputs; no sensitive publication.
- S7: "Ejecuta los tests y, si los archivos privados reales están disponibles, realiza una ejecución real del entrenamiento y generación de scores." Verify listed alignment/schema/isolation/reproducibility rules and prior EDA compatibility; distinguish real and synthetic proof.
- S8: "No hagas merge a `main`, no crees una pull request y no avances a Fase 5." "feat(ml): implement reproducible churn ranking baselines"; "git push -u origin feat/kkbox-model-baselines" only after all acceptance gates. Update progress/roadmap and documentation; final report in Spanish.

## Tasks
- T1 (S1,S2): inline; verified; deterministic baseline behavior with synthetic RED/GREEN. No writer trigger.
- T2 (S3–S7): inline; verified; strict frozen-input loader, training/scoring CLI and synthetic tests. No independent parallel write surface; Risk item 5 (new pinned ML dependencies), item 3 (dependency import-test mapping).
- T3 (S4–S8): inline; verified; real train/rebuild and EDA proof, independent verifier, aggregate documentation and privacy-reviewed commit/push. Long checks delegated per action.

## Log
- L1 (2026-10-20): User requested "Retention Lab — Phase 4: Baselines and First ML Models", complete implementation and automatic commit/push only when all stated acceptance criteria hold. The original detailed request remains the controlling scope; S1–S8 quote its binding clauses rather than expanding it.
- L2: Existing branch reuse authorized with "si". Explorer model substitution to available `gpt-6-luna` authorized with "si" after configured `gpt-6.1-luna` was unavailable. Read-only explorer loaded all mandatory project documents and mapped schemas without raw/final label access. Engram unavailable; mirror pending.
- L3: `git fetch origin` succeeded; main/origin/main/HEAD all base above; Phase 3 reference is ancestor; clean tree. RDD globally off, unchanged. Single requested branch/commit takes precedence over automatic chain/PR workflow; no PR created.
- L4: Design: single logistic candidate, binary renewal passthrough, median numeric imputation with missingness indicators and retained empty columns, numeric standardization; all learned state train-only. Separate purpose salts for random/business/ML ties. Validate frozen artifacts before training; never load raw outcomes or final labels.

- L5: Baselines RED missing module, GREEN 3 tests. Training RED: four failures/two errors from missing CLI/module (12 discovered including inherited preparation tests); GREEN after implementation. Removed duplicate discovery of imported fixture class; final local suite 53 tests passed, dependency health passed. Added quality/provenance check afterwards; focused rerun 8 passed. Dependency import mapping observed RED then adjusted sklearn→scikit-learn without relaxing explicit-pin coverage. Four ML dependency additions, original 48 pins unchanged.

- L6: Real training/scoring passed in 10.01s and 12.22s; independent output rebuild 11.98s. All 13 files byte-identical. Counts 523998/175651/174931; logistic converged in 21 iterations without warnings. Validation AP 0.335492236, ROC-AUC 0.812454660, log loss 0.160784293; business AP 0.212766910, ROC-AUC 0.780568871. Retain one logistic candidate; no second model or test-label use.
- L7: EDA --check passed in two kernels after authorized socket escalation; aggregate SHA-256 unchanged. All 52 installed distributions match pins; pip check passed. Independent verifier pending. Scratch reconstruction retained for parent cleanup.

- L8: Independent verification PASS per S1–S7; S8 administrative closure pending. Baseline42/candidate53 tests, five CLI help differentials and complete synthetic prior-preparation artifact equivalence. Integrated semantic manifest/schema/alignment probes and independent hash/fit-statistics checks into tests; model-focused9 passed. Parent spot-check real CLI matched frozen hashes. All implementation source bytes remain those of the real frozen model manifest.
- L9: Phase4 marked DONE after all analytical gates; single completion commit/push pending final full-suite, diff and privacy checks. No PR or Phase5; final-label isolation is dataflow, not OS denial. Existing platform/source/arrival/labeler limits unchanged. Engram mirror pending (unavailable).

- L10: Final full54 PASS (28.395s), model-focused9 PASS, diff whitespace PASS. Private13 file hashes and source/runner/dependency identity match real frozen run. Publication scan16 UTF-8 files PASS; no data, models, IDs, secrets or excessive files. Initial scan wrapper had an unused import-path error after checks; corrected full rerun PASS. Parent removed worker scratch after recording evidence.
- L11: T1–T3 belong to the single authorized completion commit `feat(ml): implement reproducible churn ranking baselines`; resolve its identity using `git log -1 -- odd/tasks/kkbox-model-baselines.md`. Exact SHA and confirmed remote URL are reported after commit/push, not embedded self-referentially. No PR, merge or Phase5.
