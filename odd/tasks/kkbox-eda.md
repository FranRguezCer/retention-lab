# Isolated KKBOX exploratory analysis
Branch: `feat/kkbox-eda`; baseline: `ec3e456`. Python 3.12 / unittest / clean notebook kernels.
Delivery: requested single completion commit and push, no PR. Forecast: approximately 1,000 authored lines; review slicing deferred (no PR authorized). Engram mirror unavailable.

## Specs
- S1: “Primero aislar; después explorar.” Reconstruct original-source eligibility through `20170131`; verify 874,581 candidates, 874,580 labeled identifiers, one missing label. Exact full-field deduplication in temporary SQLite; hash salt `retention-lab-feb2017-v1|`, integer modulo 10, train 0–5, validation 6–7, final 8–9. Freeze private assignments/configuration/fingerprints; reject mismatches. Only training label values may be interpreted after partition verification.
- S2: “Crear `notebooks/01_eda.ipynb` y `docs/methodology.md`, en inglés.” Training-only private input; Python 3.12 with pandas, matplotlib and notebook execution tools, no modeling dependencies. Missingness, duplicates, dates, distributions, observed history, amounts, plan duration, transaction frequency and unambiguous daily changes. Five interpreted charts (at least three defensible), three specified hypotheses; document candidate auto-renew-off rule with digest/ID tie-breaking, do not implement baseline.
- S3: “Aplicar RED → GREEN a la lógica nueva con fixtures sintéticos”. Hash, order stability, coverage/disjointness, eligibility, exact duplicates, conflicts and cutoff invariance; future expiry recorded pre-cutoff allowed. Changing non-training labels must not affect preparation or EDA. Existing tests included; no real global label auditors. Twice reconstruct, twice execute notebook from clean kernels; compare stable private assignments and aggregates. No IDs, individual rows, private paths or error outputs in published notebook.
- S4: “Actualizar `PROGRESS.md` con conteos reales, hallazgos, limitaciones, comandos y resultados. Marcar `DONE` solo con todos los criterios verificados.” Independent verification of isolation/dependencies. Preserve effective RDD mode. Final diff/privacy/size review then `analysis: complete KKBOX exploratory data analysis` and `git push -u origin feat/kkbox-eda`; no completion commit/push if proof missing. No models, Phase 3, PR or deployment.

## Tasks
- T1 [S1,S3] inline — verified; partition preparation and synthetic RED/GREEN.
- T2 [S2,S3] inline — verified; training artifact, notebook, environment and documentation.
- T3 [S3,S4] independent verifier — verified; risk items 2 (holdout isolation) and 5 (dependencies); two real preparations/kernels and privacy review.
- T4 [S4] inline — verified; delivery in completion commit (see L8); factual progress, completion commit/push only after proof.

## Log
- L1 (2026-10-19): User supplied “Fase 2 — EDA reproducible y aislado de KKBOX” implementation plan; exact requested scientific fragments are preserved in S1–S4. The original chat remains the complete plan reference.
- L2: User authorized `gpt-6-luna` instead of unavailable `gpt-6.1-luna`: “si”.
- L3: Fetch verified HEAD=origin/main=ec3e456, clean tree and no pre-existing feature branch. Branch created. RDD globally off; unchanged. Read-only explorer initialized CodeGraph, whose generated index is now ignored. Existing auditors remain untouched. Engram unavailable.

- L4: Synthetic preparation RED (four missing-CLI failures), GREEN (four pass); aggregate RED (missing module), GREEN (two pass). Full suite 20 passes. No existing auditors modified. Numerical distributions sorted before statistics to make floating-point summaries order-stable.
- L5: Real preparations exited 0 in 238/244 seconds; all four private artifacts identical. Counts train 523998, validation 175651, final 174931; candidates 874581, unlabeled 1. Parent rechecked four hashes. First two clean kernels matched all text/figures and privacy checks. Sandbox socket failure required authorized local-kernel execution outside sandbox.

- L6: Final notebook `--check` passed (two clean kernels, exact text/PNG equality and privacy), 5 figures, aggregate hash bdef546b4e271083a53d15e690d44b688c097231cafc4d65de98c5ada1a482bf. Fixed required empty output metadata after observed nbformat RED; structural test GREEN.
- L7: Independent verifier found no blockers: baseline 14/candidate 21 tests, three unchanged auditor command differentials, extended isolation/immutability probes, 68 dependency constraints and full lock installed-version compatibility passed. Added probes as regression coverage; final suite 22 passes. Official page unreadability is documented, not claimed as verified source semantics. Risk: item 2 (holdout-isolation guards), item 5 (new dependency environment).
- L8: Completion commit is the commit containing this document (`git log -1 --format=%H -- odd/tasks/kkbox-eda.md`); publication SHA and remote reference will be confirmed in final delivery. Explicit single completion commit/push from user plan; no PR or extra branches. Authored line budget overage retained for cohesive scientific artifact; review slicing can be decided before any future PR. Engram remains unavailable.

- L9: Final publication review covers aggregate-only notebook/JSON, ignored private files, unchanged main and auditor sources. Updated PROJECT/ROADMAP current statuses and appended a historical-status pointer to problem definition to prevent stale partition instructions. Final source-normalization check: git diff --check.
- L10: Final staged scan passed (19 files, aggregate-only publication; five figures; no private IDs/paths/data or secrets), staged whitespace check clean. Main/origin/main remain ec3e456, raw auditors unchanged; RDD remains off. Completion commit and push explicitly authorized by the user plan; exact remote identity is reported in chat.
