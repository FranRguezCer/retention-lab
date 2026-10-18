
---
name: retention-stage
description: Guide the incremental implementation, review and verification of a Retention Lab development stage. Use when the developer asks to start, continue, review or complete a roadmap phase. Do not use for unrelated repository questions.
---

# Retention Lab Stage Workflow

## 1. Load project context

Read:
- AGENTS.md
- PROJECT.md
- ROADMAP.md
- PROGRESS.md

Inspect the relevant existing code and tests.

## 2. Establish scope

Identify:
- Current phase
- Requested task
- Expected deliverable
- Dependencies
- Acceptance criteria
- Relevant methodological risks

Do not start unrelated tasks.

## 3. Explain before implementing

Briefly explain:
- What problem this task solves
- Relevant Data Science or engineering concepts
- The proposed approach
- Important trade-offs

For significant design decisions, present alternatives.

## 4. Implement incrementally

- Make focused changes.
- Preserve existing architecture.
- Prefer simple Python functions.
- Keep research notebooks separate from reusable code.
- Avoid speculative abstractions.
- Do not add unrelated features.

## 5. Verify

Perform the checks relevant to the task.

Examples:
- Unit tests
- Data integrity checks
- Temporal boundary checks
- ML evaluation sanity checks
- Frontend build

Distinguish tests that passed from checks not executed.

## 6. Review results

Explain:
- What was implemented
- What the evidence demonstrates
- What remains uncertain
- Any methodological limitations
- Whether acceptance criteria are satisfied

Never fabricate data, metrics or successful tests.

## 7. Update progress

Update PROGRESS.md with:
- Completed work
- Important decisions
- Verification evidence
- Blockers
- Next task

Do not mark a phase complete unless its acceptance
criteria have been verified.

## 8. Stop

Stop after the requested task.

Do not automatically start the next roadmap stage.

