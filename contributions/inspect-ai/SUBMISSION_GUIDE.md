# Upstream PR Submission Guide — Inspect AI

This guide provides step-by-step instructions for submitting the prepared
contribution artifacts as pull requests to
[UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai).

All contribution artifacts are fully prepared in this repository under
`contributions/inspect-ai/`. The steps below walk through forking the
upstream repo, creating branches, applying the content, and opening PRs.

---

## Prerequisites

- A GitHub account with contributor access (personal or org account)
- `git` installed locally
- `gh` CLI installed (optional but recommended)

---

## Step 1 — Fork the upstream repository

1. Go to https://github.com/UKGovernmentBEIS/inspect_ai
2. Click **Fork** → **Create fork** (fork into your personal account or the
   `clearedge-it` org)
3. Clone your fork locally:

```bash
git clone https://github.com/YOUR_ACCOUNT/inspect_ai.git
cd inspect_ai
git remote add upstream https://github.com/UKGovernmentBEIS/inspect_ai.git
git fetch upstream
git checkout -b main upstream/main
```

---

## PR 1 — Multi-value scorer patterns for dimensional evaluation

### Step 2a — Create the branch

```bash
git checkout -b clearedge/multi-value-scorers-docs
```

### Step 2b — Apply the content

The content to add is in
[`contributions/inspect-ai/docs/multi-value-scorers.md`](docs/multi-value-scorers.md)
in this repository.

Open `docs/scorers.qmd` in the upstream repo and insert the content from
`multi-value-scorers.md` after the "Custom Scorers" section, before the
"Scoring with Multiple Scorers" section.

The section heading to insert after is:
```
## Custom Scorers {#sec-custom-scorers}
```

The section heading to insert before is:
```
## Scoring with Multiple Scorers
```

### Step 2c — Commit and push

```bash
git add docs/scorers.qmd
git commit -m "docs: add Multi-Value Scorers section to scorer documentation

Document the pattern of returning dict[str, Score] from @scorer functions
with per-key metric lists. Includes a worked example (dimensional_scorer)
that grades a tool-calling agent across three independent dimensions:
task_completion, behavioral_safety, and process_fidelity.

Motivation: the current docs cover single-value scorers well but lack
examples of multi-value scorer composition. This pattern is useful when
an evaluation has orthogonal quality axes that should each have their own
aggregate statistics rather than being collapsed into a single number.

Closes #<issue-number-if-any>"

git push origin clearedge/multi-value-scorers-docs
```

### Step 2d — Open the PR

Go to https://github.com/UKGovernmentBEIS/inspect_ai/compare and open a PR
from `YOUR_ACCOUNT:clearedge/multi-value-scorers-docs` → `main`.

**PR title:**
```
docs: Multi-value scorer patterns for dimensional agent evaluation
```

**PR body:**
```markdown
## Summary

This PR adds a "Multi-Value Scorers" section to the scorer documentation,
demonstrating how to return `dict[str, Score]` from a `@scorer` function
with per-key metric lists.

## Motivation

The current Inspect docs cover single-value scorers well but lack examples
of multi-value scorer composition. This pattern is useful when an evaluation
has several orthogonal quality axes (e.g. task completion, behavioral safety,
process fidelity) that should each have their own aggregate statistics rather
than being collapsed into a single number.

## Changes

- Adds `## Multi-Value Scorers` section to `docs/scorers.qmd`
- Includes a worked example: `dimensional_scorer` that grades a tool-calling
  agent across three independent dimensions
- Shows how to specify per-dimension metrics using a dict in `@scorer(metrics={...})`
- Explains the difference between multi-value scorers and multiple separate scorers
- Shows how to read per-sample dimension scores from the eval log

## Example

```python
@scorer(metrics={
    "task_completion":    [mean(), stderr()],
    "behavioral_safety":  [mean(), stderr()],
    "process_fidelity":   [mean(), stderr()],
})
def dimensional_scorer(...) -> Scorer:
    async def score(state: TaskState, target) -> dict[str, Score]:
        ...
        return {
            "task_completion":   Score(value=tc),
            "behavioral_safety": Score(value=bs),
            "process_fidelity":  Score(value=pf),
        }
    return score
```

## Checklist
- [x] Documentation only (no code changes)
- [x] Worked example included
- [x] Explains when to use vs. multiple separate scorers
```

---

## PR 2 — Approval policy patterns for tool-calling agents

### Step 3a — Create the branch

```bash
git checkout main
git checkout -b clearedge/approval-policy-cookbook
```

### Step 3b — Apply the content

The content to add is in
[`contributions/inspect-ai/docs/approval-policy-patterns.md`](docs/approval-policy-patterns.md)
in this repository.

Open `docs/approval.qmd` in the upstream repo and append the content from
`approval-policy-patterns.md` after the existing "Custom Approvers" section.

The section heading to append after is:
```
## Custom Approvers {#sec-custom-approvers}
```

### Step 3c — Commit and push

```bash
git add docs/approval.qmd
git commit -m "docs: add Approval Policy Cookbook section to approval documentation

Document advanced approval policy patterns for tool-calling agents:
1. Command allowlist with argument validation
2. Docker command validation with volume mount enforcement
3. Escalation pattern detection
4. Model-assisted triage approver

Motivation: the existing approval docs show a simple bash_allowlist
skeleton but do not cover non-trivial validation flows. BasinBench's
mcp_approval_policy demonstrates Docker command validation, volume mount
enforcement, and escalation pattern detection — patterns that are useful
for any agentic evaluation with shell or container access.

Closes #<issue-number-if-any>"

git push origin clearedge/approval-policy-cookbook
```

### Step 3d — Open the PR

Go to https://github.com/UKGovernmentBEIS/inspect_ai/compare and open a PR
from `YOUR_ACCOUNT:clearedge/approval-policy-cookbook` → `main`.

**PR title:**
```
docs: Approval policy cookbook for tool-calling agents
```

**PR body:**
```markdown
## Summary

This PR adds a "Cookbook: Advanced Approval Policies" section to the
approval documentation, showing patterns for real-world approval policies
used in agentic evaluations where the agent has access to shell execution
or container management tools.

## Motivation

The existing approval docs show a simple `bash_allowlist` skeleton but do
not cover non-trivial validation flows. This cookbook fills that gap with
three patterns derived from production agentic evaluation work:

1. **Command allowlist with argument validation** — approve/escalate based
   on the base command and sudo usage
2. **Docker command validation** — enforce volume mount restrictions and
   reject privileged mode
3. **Model-assisted triage** — use a small model to handle the grey zone
   between the allowlist and human review

## Changes

- Adds `## Cookbook: Advanced Approval Policies` section to `docs/approval.qmd`
- Three complete, runnable approver implementations
- YAML policy composition examples for each pattern
- Testing section showing how to unit-test approvers without a full eval

## Checklist
- [x] Documentation only (no code changes)
- [x] Three complete worked examples
- [x] Includes testing guidance
```

---

## Step 4 — Record PR numbers in the plan

After opening both PRs, update `plans/oss-contributions.yaml` in this
repository. Replace the `upstream_prs: []` line in `phase-1-inspect-ai`
with:

```yaml
upstream_prs:
  - number: <PR1_NUMBER>
    title: "docs: Multi-value scorer patterns for dimensional agent evaluation"
    url: https://github.com/UKGovernmentBEIS/inspect_ai/pull/<PR1_NUMBER>
    status: open
    description: >-
      Adds Multi-Value Scorers section to docs/scorers.qmd with a worked
      example of dict[str, Score] return from @scorer functions.

  - number: <PR2_NUMBER>
    title: "docs: Approval policy cookbook for tool-calling agents"
    url: https://github.com/UKGovernmentBEIS/inspect_ai/pull/<PR2_NUMBER>
    status: open
    description: >-
      Adds Cookbook: Advanced Approval Policies section to docs/approval.qmd
      with three complete approver implementations and testing guidance.
```

Then update `contributions/inspect-ai/README.md` to replace the "Pending"
status rows with the actual PR numbers and links.

---

## Optional: PR 3 — Agent solver composition example

If the first two PRs are well-received, submit the example:

```bash
git checkout main
git checkout -b clearedge/agent-solver-composition-example
# Copy contributions/inspect-ai/examples/agent_solver_composition.py
# to docs/examples/ or examples/ in the upstream repo
git add docs/examples/agent_solver_composition.py
git commit -m "examples: agent solver composition cookbook

Shows how to compose multiple solver variants (baseline, chain-of-thought,
self-critique) for agent evaluation without duplicating the core agent loop.
A shared _run_agent_loop helper reduces boilerplate across variants."
git push origin clearedge/agent-solver-composition-example
```

---

## Optional: Issue — fixed_criterion for model_graded_qa

Open a GitHub issue (not a PR) using the content from
`contributions/inspect-ai/rfcs/fixed-criterion-model-graded-qa.md` as the
issue body. This is an RFC/feature request that should be discussed before
a PR is opened.

Issue title: `feat: fixed_criterion parameter for model_graded_qa`
