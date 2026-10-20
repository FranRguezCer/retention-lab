# KKBOX feasibility: restricted retrospective protocol

> **Historical Phase 1 audit and restricted decision (2026-10-19).** Branch names,
> pending checks, commands and authorization/publication boundaries below record
> that stage, not the current handoff. Phases 1–5 are now complete within the
> restricted scope; see [current results](results.md),
> [progress](../PROGRESS.md) and [publication boundary](data_attribution.md).
> Phase 6 is NOT STARTED. Do not rerun these original-source audits as part of
> documentation maintenance or reopen the consumed final test.

**Decision: RESTRICTED GO for a single-cohort, offline comparison.**
**Not approved:** an operational historical campaign or a February-to-March
forward-transfer claim. The developer explicitly accepted this restricted
contract on 2026-10-19: **Phase 1 DONE — RESTRICTED GO**. This is not
authorization to begin Phase 2.

Updated: 2026-10-19. Branch: `feat/kkbox-minimal-audit`.
This supersedes the two-file NO-GO: the original history resolves most input
coverage, but does not make training labels historically available sooner.

## 1. Official evidence, local observations and remaining inference

| Source | Evidence actually accessible | Limit |
|---|---|---|
| [WSDM official call](https://www.wsdm-conference.org/2018/call-for-participants.html) | Broad target: renewal within 30 days after expiry | Does not specify event adjudication |
| [KKBOX host, discussion 40316](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/discussion/40316) | Search-indexed host response: original training cohort has February 2017 expiries; original test has March expiries; cancellation may affect the expiry anchor | Direct page extraction was empty; thread includes unresolved participant questions and inconsistent example dates |
| [KKBOX host, discussion 43622](https://www.kaggle.com/competitions/kkbox-churn-prediction-challenge/discussion/43622) | Search-indexed host response: failure to renew within 30 days is churn; late renewals still count as churn; directs readers to supplied labeler | Not an executable rule for every event sequence |
| [Official rules, sections 7–8](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/rules) | Search-indexed official text distinguishes permitted educational/research use, data security and sharing source code | Not blanket permission to publish datasets or this project's future derived artifacts |
| [Original Kaggle data page](https://www.kaggle.com/c/kkbox-churn-prediction-challenge/data) | Destination accessible, but no readable catalog/description body | No official archive manifest, checksum or full v2 specification verified |
| [Participant description mirror](https://github.com/RyuJiseung/WSDM_2018) | Secondary lead associates `train_v2.csv` with March expiries | Not independently authenticated as the full official file specification |

**Official concept:** supplied `is_churn` is a churn outcome, not the cancellation
flag. Non-renewal within the grace period is churn; a later return does not erase
that event. Host answers support different-period labels for the same user.
**Unknown:** exact day-30 boundary, qualifying transaction rules, effective
expiry reconstruction and same-day tie ordering in the supplied Scala code.
A bounded external search did not locate an authenticated readable copy of
`WSDMChurnLabeller.scala`. No Scala file was downloaded into this repository,
no Scala runtime was added, and the labeler was not executed or ported.

**Local evidence:** the hashes, headers and counts below describe these actual
four CSVs. Names and plausible schemas do not authenticate official downloads.
The user supplied the files; no credentials, accounts or agreements were used.

**Inference kept separate:** March-expiry semantics for every `train_v2` row
remain less strongly evidenced than the original February cohort. Neither
label CSV contains its own expiry, cohort date or label-release timestamp.
The recommended experiment therefore uses the original February cohort only;
no inference about the complete v2 cohort is needed to authorize it.

### Use and publication boundary

The indexed rules list competition/forum, academic research and education as
permitted uses after acceptance, and prohibit making competition data available
to nonparticipants. They distinguish publishing one's source code from sharing
the data. The developer remains responsible for lawful acquisition, accepting
applicable terms and confirming any future publication of derived artifacts.
This audit approves neither raw-data redistribution nor a public demo dataset.
Raw files and audit reports remain local and ignored. No subscriber identifiers
or customer-level records are included here. This is not a legal clearance.

## 2. Verified four-file inventory

| File | Bytes | Rows | Unique IDs | Transaction-date coverage |
|---|---:|---:|---:|---|
| `train.csv` | 46,667,771 | 992,931 | 992,931 | No date column |
| `train_v2.csv` | 45,635,134 | 970,960 | 970,960 | No date column |
| `transactions.csv` | 1,729,298,376 | 21,547,746 | 2,363,626 | 20150101–20170228 |
| `transactions_v2.csv` | 115,394,513 | 1,431,009 | 1,197,050 | 20150101–20170331 |

Both label headers: `msno,is_churn`.
Both transaction headers, in order:
`msno,payment_method_id,payment_plan_days,plan_list_price,actual_amount_paid,is_auto_renew,transaction_date,membership_expire_date,is_cancel`.

All four passed the implemented structural checks: expected columns/row width,
nonempty fields, binary labels/flags and real ASCII `YYYYMMDD` calendar dates.
No label file has duplicate IDs or conflicting duplicate-label rows.
Numeric payment/plan semantics and every numeric column's type/range were not
validated; passing this audit is not a full semantic quality certificate.

- Original labels: 929,460 zeros and 63,471 ones.
- V2 labels: 883,630 zeros and 87,330 ones.
- Original expiry range: 1970-01-01–2017-03-31; 153,660 rows have expiry before
  transaction date. Calendar validity does not establish their business meaning.
- V2 expiry range: 2016-04-19–2036-10-15; 5,106 rows have expiry before the event,
  909 have expiry after 2020. Earlier audit found one 2036 row. None proves
  follow-up through that date; no clipping/repair is authorized.

SHA-256 of original input bytes:

- `train.csv`: `14140a13139b9952686a85b70378c106da4cef43180a3cd50a2962ce64724767`.
- `train_v2.csv`: `1f7590a3467174f5a147db3fb85dd1393074b6c13da0fd6e70af31bf37dee5cc`.
- `transactions.csv`: `537c269140742fc74b28ba83941dff7b0ca00974dd48b80994948b8917adddef`.
- `transactions_v2.csv`: `1d3015e32ed1661e9cfe813a9779b1b33e9d1d0829f1203633440045d4c6ea36`.

Latest aggregate report: `data/audit/history_sources.json`, audit version 2,
SHA-256 `4c1930bd51cddbe26e2974ec63942173bb5871a710b58b2cac5d281dd795ae8c`.
Original-only population report: `data/audit/february_population.json`, SHA-256
`632a73c4149964ed32c678abbf5047d917c339abe2f0573d34e6246d52e65741`.

## 3. What the additional history changes

`transactions.csv` adds 21,547,746 rows of dense monthly history through February
28, rather than treating v2's sparse pre-March tail as complete history.
The original file has 20,639,483 rows dated through January 31.
`train.csv` adds 992,931 unique supplied targets for the primary-evidenced
February expiry cohort. Together they support a single-cohort retrospective
study without reconstructing labels from scratch. The selected labeled subset
contains both classes: **826,393 non-churn and 48,187 churn**. This is a target
integrity/viability count, not a modeling result or EDA association.

### Transaction-file relationship

- They share **1,134,533 subscriber IDs**, not necessarily the same events.
- There are **zero matching distinct full-row SHA-256 identities** across files.
  Identity is canonical JSON of every parsed CSV field, not just user/date.
- Original file: **3,339 repeated full-row identities**, leaving 21,544,407
  distinct rows. V2 has no repeated full-row identities.
- Across both: 22,975,416 distinct full-row identities. This is a fingerprint
  comparison with the usual negligible collision assumption, not event-ID proof.
- V2 includes **1,069,822 March rows and 361,187 earlier rows**. It is not simply
  a March-only append, nor is it a byte-for-byte replacement for the original.
- Even without identical rows, releases might describe amended or related events:
  there is no event ID or ingestion timestamp establishing semantic equivalence.
  Do not collapse rows solely on user/date or automatically merge both releases
  for prediction inputs.

Adding v2's backdated rows materially changes the latest observed state. For
example, among `train_v2` IDs at February 28, the original-only non-cancelled
next-month-expiry count is **938,138**, versus **854,177** using the union.
This is not proof of corrections or errors; it is evidence that concatenation
is not innocuous. The selected protocol freezes **original-source inputs only**.

### Label-file relationship

| Original → V2 label among shared IDs | Count |
|---|---:|
| 0 → 0 | 824,659 |
| 0 → 1 | 40,721 |
| 1 → 0 | 5,269 |
| 1 → 1 | 11,052 |

There are **881,701 shared IDs**, 111,230 original-only and 89,259 v2-only;
45,990 shared users have different labels. These are not duplicate targets
that should be overwritten: different outcome windows can produce different
labels. Exact per-user expiry anchors were not reconstructed. A naive row
split after concatenating label files risks subscriber contamination.

## 4. Cutoff checks and record-state limits

A diagnostic snapshot uses the greatest transaction date on/before the cutoff.
If that day's records disagree on `(membership_expire_date,is_cancel,is_auto_renew)`,
the state is ambiguous; no arbitrary row wins. Matching states do not resolve
possible ties in payment amounts or other fields. No predictive features or
subscriber-level output table was built.

Original-source results (not the union):

| Cutoff / label file | With history | Latest state unambiguous, expiry next month | Also `is_cancel=0` |
|---|---:|---:|---:|
| Jan 31 / original labels | 990,834 | 877,769 | 874,580 |
| Jan 31 / v2 labels | 937,817 | 782,558 | 781,586 |
| Feb 28 / original labels | 992,931 | 884,893 | 881,775 |
| Feb 28 / v2 labels | 968,433 | 941,519 | 938,138 |

The original-source latest day is ambiguous for 56,465 users at January 31 and
56,433 at February 28; those are all-source-user counts, not labeled-user counts.
For original labels at January 31, 2,097 have no history and 11,342 have ambiguous
latest-day states. The remaining exclusions from the selected cohort arise from
the explicit next-month expiry / non-cancellation conditions, not target value.

`membership_expire_date` is treated here as an **observed record field**, not a
proven final entitlement or churn date. `is_cancel` is a transaction flag, not
`is_churn`; cancellation can affect an expiry anchor or be followed by renewal.
`is_auto_renew` indicates observed renewal configuration, not a guaranteed future
payment. Same-day ordering and distant dates remain unresolved operationally.
Future renewal/cancellation events must never be brought into cutoff inputs.

## 5. Recommended restricted contract — February single-cohort benchmark

This is deliberately narrower than a February→March campaign backtest.
`PROJECT.md` explicitly permits a limited retrospective comparison at the Phase 1
gate. The trade-off is clear: a valid held-out comparison on a named historical
population, but no claim about prospective deployment or month-to-month transfer.

| Element | Contract |
|---|---|
| Prediction index | Start of 2017-02-01, using calendar-day event dates; not a claim the model existed then |
| Input vintage | `transactions.csv` only; no v2 transactions, v2 labels, profiles or activity inputs |
| Input cutoff | `transaction_date <= 20170131`; event date is a retrospective proxy, not verified arrival time |
| Candidate population | From the original transaction source alone: latest observed day has a single expiry/cancel/auto state; recorded expiry in Feb 1–28; `is_cancel=0` on that state |
| Observed candidate count | 874,581 users, defined without their outcome values |
| Labeled study population | The 874,580 candidates with a supplied `train.csv` label; one candidate lacks a label and is excluded from evaluation, explicitly reported |
| Target | Supplied original February-cohort `is_churn`, not a label generated from the snapshot expiry or cancellation flag |
| Horizon | Official February-expiry outcome, with renewal observation extending up to March 30 for a Feb 28 anchor; not simply churn in February or 30 days after prediction |
| Training availability | Fit retrospectively only after outcomes are supplied/mature. Full February cohort requires observation through March 30 and conservatively March 31 plus processing lag; actual release time unknown |
| Development / final holdout | One subscriber per observation. Before EDA, freeze deterministic subscriber partitions: SHA-256 of `retention-lab-feb2017-v1|` + ID, interpreted as an integer modulo 10; 0–5 train, 6–7 validation, 8–9 final evaluation. IDs are partition keys only, not predictors or exports |
| Tuning and comparison | Fit preprocessing on training only; select baseline/model on development only; all three policies use exactly the same final labeled population and capacities |
| Duplicate policy | For later processing, retain one identical full-field record within this input vintage; do not use user/date alone as an event key; document possible loss of indistinguishable genuine events |
| Latest-field policy | Use latest expiry/cancel/auto only where the diagnostic agreement rule holds. Other latest-field features require separate tie checks; no hidden file-order tie-breaking |

This contract defines **record-based eligibility for the study**, not proof of
the entire active paid subscriber population at that historical date. Matching
supplied labels still conditions the estimand on the competition cohort. Outcome
values are not used for eligibility or partitioning; supplied target semantics
are accepted as benchmark outcomes, not independently regenerated business truth.
The date filter, source vintage and selection rule must be regression-tested
when actually building tables in Phase 3; this audit does not implement them.

Example: a January 31 record shows a non-cancelled February 28 expiry, and its
latest-day state is unambiguous. It is a candidate for the February 1 index.
A February renewal or cancellation is future information, never an input.
The supplied cohort outcome may require follow-up through March 30. Training a
model later using that outcome can support a retrospective held-out benchmark;
claiming that model was ready on February 1 would be false. This follows ordinary
30-day date arithmetic; exact day-boundary and release details remain unverified.

### Why not approve an operational or cross-cohort backtest?

Even training on February expiry labels for a March 1 campaign uses labels that
may need March follow-up. January 31 + 30 days is March 2; even a whole January
cohort is not automatically mature at March 1. A March 31 expiry would need
observation through April 30 plus lag. Public competition release dates are not
historical internal label-availability timestamps.

An operational model would need genuinely earlier mature outcomes, official
state/event rules and arrival/completeness evidence. Reconstructing that entire
history is disproportionate for the selected portfolio increment. The four
files alone do not prove those conditions. An original→v2 retrospective temporal
comparison also needs authenticated v2 cohort dates, subscriber-overlap policy
and explicit vintage semantics before it can replace the chosen benchmark.

## 6. Leakage controls, limitations and remaining work

| Risk | Control / status for the selected benchmark |
|---|---|
| Post-cutoff transactions | Reject all original events after Jan 31 for inputs; no v2 input at all |
| Backdated later-release records | Avoid release fusion; original-source vintage is frozen |
| Retrospective eligibility | Use pre-cutoff record criteria first, then report the one missing supplied label; no claim about the full operational population |
| Unavailable training labels | Fit only retrospectively; explicitly prohibit simulated historical model-readiness claims |
| Same user in different label files | Do not concatenate target files; final test is subscriber-disjoint within the one chosen cohort |
| Cancellation interpreted as target | Use supplied labels; cancellation is only an explicit pre-cutoff subset condition |
| Same-day ordering | Exclude ambiguous selected-state days; no arbitrary last row |
| Duplicate events | Explicit full-field duplicate policy; no destructive changes to originals |
| Large/distant expiry values | No invented repairs; 1970 and 2036 remain data-quality questions; current population filter is predeclared, not performance-selected |
| Outcome selection / final-label reuse | Only integrity aggregates inspected here; no ranking, model or rule was selected by final outcomes |
| Event arrival, logging completeness and source authenticity | Not proved; restrict claims to recorded-event retrospective evidence |
| Public use/redistribution | Developer confirms applicable terms before future publication; no data published here |

Remaining **implementation checks**, not reasons to reconstruct KKBOX infrastructure:
freeze and record actual split counts before EDA; keep final labels inaccessible
to development; verify subset/source/cutoff/duplicate rules through the public
processing interface when introduced; investigate numeric fields before using
them; report cohort/coverage limits beside every future metric. No three-curve
results exist yet and none are fabricated. No detected churner is claimed saved.

Remaining **blockers for broader claims**, not approved by this decision:
authenticated complete v2 cohort description, Scala adjudication semantics,
historical mature training labels and ingestion-time availability. Publication
of raw or derived data remains a separate permissions question. No additional
massive file, activity data, Scala dependency or outcome regeneration is needed
for the chosen supplied-label benchmark.

## 7. Verification and next phase boundary

- New `scripts/audit_kkbox_history.py`: standard library; reuses the legacy
  auditor's schemas and fingerprint helper without changing legacy behavior.
- Strict structural/aggregate audit of all four actual files passed. Version 1
  ran in about 201 seconds; version 2 added original-only snapshots and ran in
  about 211 seconds. Both verified raw SHA-256 unchanged before/after. Memory
  scales with unique row hashes and users (several GB expected, peak not measured).
- New synthetic tests observed RED before implementation; source-isolation
  assertion also observed RED before the original-only summary was added.
- Focused history audit tests: **7 passed**; full suite: **14 passed**, also
  recorded in `PROGRESS.md`. Coverage includes source isolation, row overlap /
  duplicates,
  label overlap, cutoff exclusion, ambiguous states, invalid fields, repeatability,
  source changes, missing/schema failures, raw/report collision protection and
  target-class viability in the original-only subset.
- Targeted original-population audit: exit 0, about 40 seconds on its first
  run; both target classes verified. The parent reran the same command: exit 0,
  existing report bytes identical and source fingerprints unchanged.
- Report rerun identity was also verified on synthetic files. The real full
  version-2 audit ran once, not twice; its source hashes were checked before/after.
- `git diff --check`: passed. Raw sources and local reports are ignored; no raw
  files are tracked. RDD was checked and remains globally off; no review started.
- No labels were regenerated, no partitions or model table materialized, no
  EDA/features/models/frontend/dependency installation/Scala/commit/push.
- Existing uncommitted skill/registry work and prior documentation history in
  `PROGRESS.md` were preserved. Engram tools remain unavailable; no memory save
  or project resolution is claimed.

Reproduce the full four-file audit (several minutes and several GB RAM):

```sh
python3 -m unittest discover -s tests -v
python3 scripts/audit_kkbox_history.py --report data/audit/history_sources.json
python3 scripts/audit_kkbox_history.py --population-only --report data/audit/february_population.json
sha256sum data/raw/train.csv data/raw/train_v2.csv data/raw/transactions.csv data/raw/transactions_v2.csv data/audit/history_sources.json
git diff --check
```

Existing reports are create-or-compare, never overwritten with different
content; use a new report path after changed sources/configuration/version.
The full audit requires all four inputs; population-only mode reads just the
original pair and avoids the large row-hash sets. No identifiers or individual
event rows are written to reports, stdout or normal validation errors. Existing two-file
`audit_kkbox.py` remains available unchanged.

**Phase 1 closure:** developer acceptance is recorded in `PROGRESS.md`.
After separate Phase 2 authorization, the first small task is to materialize
and verify the specified deterministic user partitions before EDA or access to
final evaluation labels: record counts, repeatability, disjointness and complete
population coverage without outcome values, and isolate final labels from
development. Partitions have not yet been materialized or verified. Later EDA
uses development users only. No Phase 2 work is performed by this closure.


### Subsequent Phase 2 status (2026-10-19)

The Phase 1 closure and next-step statements above are historical. Phase 2 was
subsequently authorized: partitions were frozen and reproduced, training-only EDA
was verified, and no validation/final outcome prevalence was inspected by that
flow. See [methodology](methodology.md) and the final Phase 2 entry in
[progress](../PROGRESS.md). Phase 3 was subsequently authorized and completed;
see the seven-predictor [feature contract](features.md). The original authorization
boundaries above are historical, not the current project status.
