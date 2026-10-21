# Interactive retention demo
Objective: implement the explicitly authorized Phase 7 static dashboard only.
Branch: feat/retention-interactive-demo; base: 787534281c9d53914bb72b17b1935f385db844cc. Delivery: single authorized branch, no PR/merge/deploy; forecast ~1,200 authored lines plus generated lockfile. Runner: Vitest, Playwright and existing Python unittest/public audit.

## Specs
- S1: "React + TypeScript + Vite"; "La aplicación debe ser **100 % estática**." Build under `web/`, strict types, no backend or model execution.
- S2: "No inventes puntos intermedios." Use the original public comparison and robustness JSON; validate all 101 exact capacities, common population, floor K, nulls, metrics and strategies.
- S3: "Churn Captured vs. Outreach Capacity"; "Subscribers selected (%)"; "Observed churners identified (Recall, %)". Four simultaneous curves, tooltip, legend and selected marker without smoothing.
- S4: "Outreach capacity"; "0 % – 100 %"; "1 %"; "10 %". Exact slider records and 5/10/20 shortcuts update all comparisons. Show K, effective capacity and expected random counts; null is N/A.
- S5: "Identifying churn does not mean preventing churn." Explain Recall/Precision/Lift, post-hoc LR, validation-selected HGB, retrospective cohort and conditional bootstrap only at 5/10/20.
- S6: "Sin scroll horizontal accidental." Responsive accessible UI, keyboard controls, visible focus, chart description and tabular alternative, loading and errors.
- S7: "npm ci"; "npm run typecheck"; "npm run test"; "npm run build". Verify frontend, Python tests/public audit, privacy, desktop/mobile browser if available; document actual evidence.
- S8: "No hagas merge a `main`."; "No abras una Pull Request."; "No comiences la Fase 8." Prepare Netlify but do not deploy; update public docs, commit/push authorized branch, verify remote SHA and clean tree. Phase7 not DONE without required deploy.

## Tasks
- T1 [S1,S2,S7] inline — complete, b486e01; validated aggregate data layer with regression tests. Risk: item 5 (new frontend dependencies).
- T2 [S3,S4,S5,S6,S7] inline — complete, b486e01; dashboard and interaction/accessibility tests. No independent writer units: UI depends on data contract.
- T3 [S7,S8] inline + independent verification — complete, b486e01 + documentation delivery record; static deployment configuration, documentation, privacy/browser/Python checks and SSH publication. Risk: item 5 (Netlify build configuration).

## Log
- L1 (2026-10-21): Authorized request: "Implementa, verifica, documenta, comitea y publica la rama autorizada." Full numbered Phase 7 requirements are in the originating conversation; quoted acceptance strings above preserve the operational specification. No Phase8, PR, merge or deployment authorized.
- L2: Clean main and origin/main verified by authorized SSH fetch; both equal base. Branch created from origin/main. CodeGraph synced; no existing frontend. All required documentation and artifacts inspected by read-only explorer; schema spot checked by parent. RDD status: off, decided by global; no native review will start.
- L3: Memory tools unavailable; local logbook is authoritative recovery context. No memory mirror available. Test-first applies to deterministic data and UI behavior; passive docs/config receive structural/build checks. Full unchanged Python suite and public-only audit will not access original data.

- L4: First runnable frontend is one cohesive delivery, ~1,100 authored lines
  excluding generated lockfile; retained code/tests/docs together rather than
  artificial per-file-type slices. User explicitly forbids PRs; deliver on the
  single authorized feature branch. No PR chain created.
- L5: Initial RED: missing App/data modules. GREEN: 26 initial unit/integration
  tests; production build and original/shipped JSON identity/privacy checks pass.
  4 Chromium tests pass (1440/768/390, keyboard, axe, load failure), screenshots
  inspected. Desktop/tablet/mobile show all four curves without overflow.
- L6: Independent fresh scratch verifier: 84 Python tests PASS, public audit PASS,
  Node24.22.0 build/check PASS; all 43 historical paths byte-identical. One
  blocker reproduced: impossible full-population counts accepted despite coherent
  formulas. RED regression observed; lower feasible bound fixed; 27 full tests
  PASS. Narrow independent recheck 24 data tests PASS and original probe rejected.
  No other blocker. Existing CLI differential N/A because no existing CLI/shared
  Python code changed. Browser libraries provisioned in temporary storage only.
- L7: README/PROJECT/ROADMAP/PROGRESS/web guide/methodology current state updated;
  46 relative documentation destinations checked. Phase7 implementation verified,
  deployment pending; Phase8 NOT STARTED. No native review: globally disabled.
  Next: final normal npm ci/checks, staged privacy readback, authorized commit/push
  and exact SSH remote SHA comparison. Rollback boundary is new web/, netlify.toml
  and associated documentation only; historical evaluation is untouched.

- L8: Final normal npm ci, typecheck, 27 tests, build, shipped JSON integrity and
  4 Chromium checks PASS. Parent public audit spot check PASS. Staged privacy and
  package-lock consistency PASS. Committed b486e01def31557d9d39b0ae3955967ec782dd69,
  pushed authorized feature branch, and verified exact remote equality. Local
  and remote main remain original base; worktree clean before this factual
  documentation closeout. No PR/merge/deploy/Phase8. All S1–S8 in authorized
  implementation scope satisfied; separate Netlify deployment remains pending.
