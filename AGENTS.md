
# Retention Lab — Repository Instructions

## Project context

Retention Lab is a Data Science and Machine Learning portfolio project.

The objective is to evaluate how much ML improves the identification
of future subscription churners when a business can only contact
a limited percentage of its subscribers.

Read these files before starting substantial work:
- PROJECT.md — scope, methodology, dataset and business narrative.
- ROADMAP.md — development phases and acceptance criteria.
- PROGRESS.md — current state, decisions and unresolved issues.

## Working agreement

- Communicate with the developer in Spanish.
- Use English for code, identifiers, docstrings and public documentation.
- Implement only the requested phase or task.
- Do not advance to another phase without explicit authorization.
- Prefer small, verifiable changes over large implementations.
- Inspect existing code before modifying it.
- Explain important technical decisions and trade-offs.
- Preserve existing work unless a change is explicitly justified.
- Do not add dependencies without a concrete reason.
- Do not overengineer.

## Learning-first development

This project is also intended to strengthen the developer's
Data Science and Machine Learning skills.

For non-trivial tasks:
1. Explain the purpose and relevant concepts.
2. Propose a small implementation plan.
3. Implement the agreed scope.
4. Run appropriate checks.
5. Explain the results and remaining limitations.

Do not generate an entire phase if the requested task is smaller.

## Python standards

- Prefer simple, modular, readable Python.
- Use type hints for reusable functions.
- Add docstrings for public functions and non-obvious logic.
- Follow PEP 8 conventions.
- Keep exploratory analysis in notebooks.
- Put reusable data processing, training and evaluation in src/.
- Use deterministic random seeds where applicable.
- Keep configuration explicit.
- Avoid unnecessary abstractions and large class hierarchies.
- Never silently swallow errors.

## Machine Learning integrity

- Never use information unavailable at prediction time.
- Respect chronological boundaries and label availability.
- Fit preprocessing only on training data.
- Keep the final evaluation data isolated from model selection.
- Evaluate all strategies on the same eligible population.
- Compare ML against random and meaningful rule-based baselines.
- Do not optimize exclusively for accuracy or ROC-AUC.
- Prioritize Recall@K, Precision@K and Lift@K.
- Never invent experimental results.
- Distinguish observed results from assumptions.
- Never claim that detected churners were saved or retained.
- Document uncertainty, methodological limitations and leakage risks.

## Data handling

- Raw datasets must not be committed.
- Respect source licensing and competition rules.
- Do not publish subscriber identifiers or personal records.
- Public demo artifacts should contain validated aggregate metrics.
- Synthetic data may be used for tests and UI mockups only.
- Never present synthetic metrics as empirical results.

## Frontend standards

- React + TypeScript + Vite.
- Deploy the static application to Netlify.
- Prefer precomputed evaluation artifacts over a backend API.
- Focus on the three strategy curves and capacity selector.
- Keep the interface accessible, responsive and understandable.
- Do not introduce authentication, databases or server functions
  without explicit authorization.

## Testing and verification

- Add focused tests for non-trivial reusable logic.
- Test temporal feature boundaries.
- Test evaluation metric calculations and edge cases.
- Run relevant tests after changes.
- Report commands executed, results and checks not run.
- Do not claim success without verification.

## Scope boundaries

Do not introduce:
- LLM agents or RAG.
- Kubernetes or microservices.
- Production CRM integrations.
- Automated retention campaigns.
- Real-time model serving.
- Uplift modeling or causal retention claims.

These require separate approval.

## Completion and handoff

At the end of each task:
1. Summarize what changed.
2. List files modified.
3. Report verification results.
4. Explain important design decisions.
5. Identify unresolved issues.
6. Update PROGRESS.md with factual progress.
7. State the next suggested task without implementing it.

Do not commit, push or deploy unless explicitly requested.

