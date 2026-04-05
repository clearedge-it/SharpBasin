# Inspect AI Upstream PR Tracking

This file tracks the actual upstream PRs opened against
[UKGovernmentBEIS/inspect_ai](https://github.com/UKGovernmentBEIS/inspect_ai).

## Confirmed PRs

### PR #3555 — MERGED ✅

**Title:** docs: document `{criterion}` variable usage in `model_graded_qa`

**URL:** https://github.com/UKGovernmentBEIS/inspect_ai/pull/3555

**Opened:** 2026-03-21

**Merged:** 2026-03-23 by @jjallaire (Inspect AI maintainer)

**Description:**
- Adds a "Template Variables" section to the Model Graded scorers documentation
- Documents where `{question}`, `{criterion}`, `{answer}`, and `{instructions}` are populated from
- Documents the key insight that `{criterion}` comes from `Sample.target`
- Provides two worked examples:
  - Dataset-driven criterion for factual QA
  - Fixed-criterion custom template for behavioral assessments (sycophancy detection)
- Closes upstream issue #1981

**Contribution type:** Documentation

---

## Pending PRs

### Multi-Value Scorers Documentation

**Target file:** `docs/scorers.qmd`

**Content:** [contributions/inspect-ai/docs/multi-value-scorers.md](docs/multi-value-scorers.md)

**Status:** Ready to submit — requires manual submission via fork

**Description:**
Adds a "Multi-Value Scorers" section documenting the `dict[str, Score]` return
pattern with per-key metric lists. Includes a worked example of dimensional
agent evaluation across three independent dimensions.

### Approval Policy Patterns

**Target file:** `docs/approval.qmd`

**Content:** [contributions/inspect-ai/docs/approval-policy-patterns.md](docs/approval-policy-patterns.md)

**Status:** Ready to submit — requires manual submission via fork

**Description:**
Adds an "Advanced Approval Policies" cookbook section documenting:
- Command allowlist with argument validation
- Docker command validation with volume mount enforcement
- Model-assisted triage for borderline tool calls
- Composing approvers in a policy chain

---

## Note on plan/oss-contributions.yaml

The `plans/oss-contributions.yaml` file on this branch contains a placeholder
entry for PR #3638 in `upstream_prs`. This is a placeholder number that should
be replaced with the actual PR number when the multi-value scorers documentation
PR is opened against the upstream repo.

**Only PR #3555 is a confirmed, real upstream PR.**
