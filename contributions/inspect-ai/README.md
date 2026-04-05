# Inspect AI Upstream Contributions

This directory contains contribution artifacts prepared for submission to
[UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai).

Each contribution is derived from patterns developed in BasinBench and
generalised for the broader Inspect AI community.

## Contributions

| Type | Title | File | Status |
|------|-------|------|--------|
| Documentation | Multi-value scorer patterns for dimensional evaluation | [docs/multi-value-scorers.md](docs/multi-value-scorers.md) | Ready for PR |
| Documentation | Approval policy patterns for tool-calling agents | [docs/approval-policy-patterns.md](docs/approval-policy-patterns.md) | Ready for PR |
| Example | Agent solver composition cookbook | [examples/agent_solver_composition.py](examples/agent_solver_composition.py) | Ready for PR |
| RFC / Feature | `model_graded_qa` with fixed-criterion templates | [rfcs/fixed-criterion-model-graded-qa.md](rfcs/fixed-criterion-model-graded-qa.md) | Open issue first |

## Motivation

BasinBench uses Inspect AI for structured evaluation of tool-calling agents
across three independent dimensions (task completion, behavioral safety, process
fidelity). In building BasinBench we encountered several patterns that are not
covered in the existing Inspect documentation or examples:

1. **Multi-value scorers** — returning a `dict` from `@scorer` with per-key
   metric lists enables independent mean/stderr tracking across evaluation
   dimensions. The current docs cover single-value scorers well but lack a
   worked example of this pattern.

2. **Approval policies for tool-calling agents** — the `@approver` decorator
   supports non-trivial validation flows (Docker command validation, volume
   mount enforcement, escalation pattern detection) that are not covered in
   the existing approval documentation.

3. **Solver composition** — the pattern of composing a base solver with
   chain-of-thought and self-critique variants via a shared `_run_agent_loop`
   helper reduces duplication and is useful for any agent evaluation.

4. **Fixed-criterion grading** — behavioral safety and process fidelity
   evaluations use the same rubric for every sample. A first-class
   `fixed_criterion` parameter in `model_graded_qa` would make this pattern
   explicit and reduce template boilerplate.

## Upstream PR Tracking

| PR | Description | Status |
|----|-------------|--------|
| TBD | Multi-value scorers + approval policy docs | Pending |
| TBD | Agent solver composition example | Pending |
| TBD | fixed_criterion RFC / issue | Pending |
