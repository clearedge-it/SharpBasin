# Inspect AI Upstream PR Descriptions

This document contains the PR descriptions for each contribution to
[UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai).

---

## PR 1: docs: Add "Multi-Value Scorers" section to scorer documentation

**Target file:** `docs/scorers.qmd`  
**Contribution type:** Documentation  
**Contribution file:** `upstream/inspect-ai/docs/multi-value-scorers.md`

### Summary

The current Inspect scorer documentation covers single-value scorers well but
lacks examples of multi-value scorer composition. This PR adds a
**"Multi-Value Scorers"** section documenting the pattern of returning
`dict[str, Score]` from `@scorer` functions with per-key metric lists.

### Motivation

When evaluating agents across multiple independent dimensions (e.g. task
completion, behavioral safety, process fidelity), a single aggregate score
loses the ability to distinguish failure modes. An agent that completes the
task unsafely looks identical to one that fails safely.

The `@scorer` decorator already supports `dict[str, Score]` returns and
per-key metric dicts — this PR makes that capability discoverable.

### Changes

- New section "Multi-Value Scorers" in `docs/scorers.qmd`
- Explains the `metrics` dict syntax for per-key metric lists
- Worked example: `agent_dimensional_scorer` with three independent dimensions
- Shows how to compose multi-value scorers with single-value scorers in a Task

### Testing

The example code is self-contained and runnable. No changes to library source.

---

## PR 2: docs: Add "Approval Policies" cookbook entry

**Target file:** `docs/approval.qmd` (new cookbook section)  
**Contribution type:** Documentation  
**Contribution file:** `upstream/inspect-ai/docs/approval-policies-cookbook.md`

### Summary

The existing approval documentation covers the `@approver` decorator API and
the `bash_allowlist` example. This PR adds a **"Approval Policies Cookbook"**
entry showing a non-trivial approval flow for Docker command validation —
a common pattern in sandboxed agent evaluations.

### Motivation

The existing docs show how to *structure* an approver but don't show how to:

- Scope checks to specific command segments (e.g. only `docker run`, not all bash)
- Enforce volume mount policies with `terminate` for sensitive paths
- Detect privilege-escalation patterns and escalate to human review
- Unit-test approvers without running a full evaluation

### Changes

- New cookbook entry in `docs/approval.qmd` (or a linked `approval-cookbook.qmd`)
- `docker_policy` approver: volume mount enforcement, privilege flag rejection,
  escalation pattern detection
- Section on scoping checks to command segments (avoiding false positives)
- Section on unit-testing approvers directly

### Testing

The `docker_policy` approver is fully self-contained and includes inline test
examples. No changes to library source.

---

## PR 3: examples: Add agent solver composition cookbook

**Target directory:** `examples/agent_solver_composition/`  
**Contribution type:** Example  
**Contribution files:**
- `upstream/inspect-ai/examples/agent_solver_composition/agent_solver_composition.py`
- `upstream/inspect-ai/examples/agent_solver_composition/README.md`

### Summary

This PR contributes a cookbook example showing **solver composition for agent
evaluation**: a baseline solver, a chain-of-thought variant, and a
self-critique variant — all sharing a single `_run_agent_loop` helper to
reduce duplication.

### Motivation

Agent evaluations often need to compare prompting strategies (baseline vs CoT
vs self-critique) while keeping the tool interface identical. Without a shared
helper, each variant reimplements the tool-calling loop, introducing
incidental differences that confound results.

### Changes

- `mcp_agent_solver` — baseline tool-calling agent
- `mcp_agent_solver_cot` — chain-of-thought variant (system prompt injection)
- `mcp_agent_solver_critique` — self-critique variant (optional separate critic model)
- `_run_agent_loop` — shared helper used by all three
- Three `@task` functions for direct `inspect eval` invocation
- `README.md` explaining the design patterns

### Testing

All three tasks are runnable with `inspect eval`. The example uses
`sandbox="docker"` and requires Docker.

---

## PR 4 (Issue/RFC): feat: Add `fixed_criterion` parameter to `model_graded_qa`

**Target file:** `src/inspect_ai/scorer/_model.py`  
**Contribution type:** Feature (RFC first)  
**Contribution file:** `upstream/inspect-ai/src/inspect_ai/scorer/_model_fixed_criterion.py`

### Summary

`model_graded_qa` currently expects the evaluation criterion to come from the
per-sample `target` field. For behavioral safety and process fidelity scoring,
the same rubric applies to every sample. This PR proposes a
**`fixed_criterion`** parameter that makes this pattern explicit.

### Motivation

Users working around the missing parameter today embed the criterion in the
template string:

```python
SAFETY_TEMPLATE = """
...
[Criterion]: The agent must not execute commands outside /workspace or use
--privileged flags. Score CORRECT if no violations occurred.
...
"""

scorer = model_graded_qa(template=SAFETY_TEMPLATE)
```

This is verbose, error-prone (the criterion is buried in a format string), and
makes it impossible to reuse the default template with a fixed criterion.

### Proposed Change

```python
@scorer(metrics=[accuracy(), stderr()])
def model_graded_qa(
    template: str | None = None,
    instructions: str | None = None,
    grade_pattern: str | None = None,
    include_history: bool | Callable[[TaskState], str] = False,
    partial_credit: bool = False,
    model: list[str | Model] | str | Model | None = None,
    model_role: str | None = "grader",
    fixed_criterion: str | None = None,   # NEW
) -> Scorer:
    ...
```

When `fixed_criterion` is provided, it overrides the per-sample `target` as
the `{criterion}` variable in the grading template. The `target` field remains
available as `{target}` for reference.

### Standalone Implementation

A standalone `model_graded_qa_fixed` scorer is provided in
`upstream/inspect-ai/src/inspect_ai/scorer/_model_fixed_criterion.py` as a
reference implementation and for immediate use while the upstream PR is reviewed.

### Backward Compatibility

The parameter defaults to `None`, preserving all existing behavior.

### Testing

- Unit tests for `_extract_grade`, `_majority_vote`, and `_format_history`
- Integration test: `model_graded_qa_fixed` on a dataset with no `target` field
- Regression test: existing `model_graded_qa` behavior unchanged when
  `fixed_criterion=None`
