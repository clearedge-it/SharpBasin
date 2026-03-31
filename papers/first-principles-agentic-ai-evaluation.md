# First Principles for Evaluating Agentic AI Systems: How SharpBasin's BasinBench Integrates Inspect, PyRIT, and Dioptra for Government-Grade AI Assessment

**ClearEdge IT Solutions, LLC** | White Paper | March 2026

---

## The Evaluation Gap for Agentic AI

Traditional AI evaluation measures model outputs against static ground truth. But the shift from passive models to autonomous agents — systems that invoke tools, access external data, and execute multi-step tasks — breaks this paradigm. An agent that produces a correct final answer through an unsafe reasoning path (exfiltrating data, exceeding authorization, bypassing safety boundaries) represents a failure that output-only scoring cannot detect. Meanwhile, adversaries have already demonstrated almost fully agentic AI campaigns in the cyber domain, underscoring the urgency of evaluation infrastructure that can keep pace.

Government evaluators need to assess three dimensions simultaneously: **task completion** (did the agent achieve the objective?), **behavioral safety** (did it respect defined boundaries?), and **process fidelity** (did it use appropriate tools and reasoning paths?). No single evaluation framework addresses all three. **SharpBasin** — ClearEdge's AI assessment platform — addresses this through its **BasinBench** evaluation suite, which composes two complementary open-source frameworks — UK AISI's **Inspect** for structured evaluation workflows and Microsoft's **PyRIT** for adversarial red-teaming — and integrates with NIST's **Dioptra** for AI Risk Management Framework-aligned trustworthiness tracking and audit export. The harness is anchored by three first principles.

## Principle 1: Evaluation Must Be Compositional, Not Monolithic

BasinBench treats evaluation as a pipeline of independent, swappable modules rather than a single scoring function. The architecture mirrors the Model Context Protocol (MCP) pattern ClearEdge uses across its agent systems: each evaluation stage (task orchestration, scoring, adversarial probing, human review) connects through a standardized interface, enabling operators to reconfigure evaluation workflows without re-engineering the harness.

**Inspect** provides the compositional backbone. Its `Task → Solver → Scorer` pipeline maps directly to the three-dimensional evaluation model: solvers orchestrate agent execution (capturing tool invocations and decision traces), while scorers evaluate task completion, behavioral safety, and process fidelity independently. BasinBench extends Inspect's `model_graded_qa` scorer with domain-specific grading criteria — including fixed-criterion templates for behavioral assessments where no per-sample ground truth exists — enabling government evaluators to define mission-specific scoring rubrics without writing custom scoring code.

**Grader independence** is a design requirement, not an afterthought. BasinBench uses a separate model for LLM-graded scoring than the model under evaluation — preventing the self-grading bias that occurs when a model rates its own outputs. The grader model is configurable per evaluation run, and concordance between heuristic and LLM-based grading methods is tracked to validate scoring consistency.

## Principle 2: Adversarial Testing Must Run Continuously, Not as a Separate Phase

Traditional red-teaming treats security testing as a gate review — a one-time event before deployment. Agentic systems, which dynamically compose tool calls and reasoning chains, can exhibit novel failure modes under adversarial pressure that did not exist during initial testing. BasinBench integrates adversarial evaluation as a continuous, automated layer rather than a discrete phase.

**PyRIT** provides the adversarial engine. Its orchestrator-converter-scorer architecture automates attack pattern execution across nine categories — prompt injection, goal hijacking, tool misuse, boundary violation, data exfiltration, privilege escalation, authority impersonation, indirect injection, and multi-turn persistence — all specific to agentic failure modes. BasinBench's adversarial probe suite (39 probes across 9 categories, defined in YAML for extensibility without code changes) feeds through the same agent sandbox used for functional evaluation, producing unified scoring across both functional and adversarial dimensions with severity-weighted resistance rates. When an agent that passes all functional benchmarks fails under adversarial pressure, the evaluation pipeline flags the discrepancy automatically.

The result is a continuous red-team loop: as new agent capabilities are deployed, adversarial probes are re-executed against updated agent configurations, and robustness trends are tracked over time through BasinBench's monitoring pipeline.

Recent implementation cycles further operationalized this loop through PyRIT-inspired attack/converter composition and standardized adversarial execution modes. In addition to baseline runs, operators now execute adversarial-variant and adversarial-scenario modes under a common evaluation approach, then compare outcome deltas in a unified reporting view.

## Principle 3: Benchmarks Must Resist Gaming While Remaining Interpretable

The sophistication of agentic AI introduces a new category of gaming risk: agents that optimize for benchmark-specific patterns without developing genuine capability. BasinBench addresses this through a gaming resistance framework with four mechanisms at two maturity levels:

**Implemented:**

- **Behavioral consistency checks** — comparing model performance across evaluation tiers for the same question namespaces, flagging models where per-namespace scores diverge by more than 20% between tiers. Consistent performance across tier sizes indicates genuine capability rather than tier-specific pattern matching.
- **Contamination detection** — comparing model performance on the standard evaluation set against a held-out set containing questions absent from all public tiers. A significant performance drop on the holdout set validates genuine capability; equivalent performance suggests the model has not memorized benchmark content.

**Planned (roadmap):**

- **Dynamic benchmark rotation** — periodically refreshing evaluation tasks to prevent memorization
- **Held-out evaluation set rotation** — rotating undisclosed test items across evaluation cycles

Implemented mechanisms run alongside functional benchmarks and produce gaming resistance scores in every evaluation report. Government evaluators receive not just a capability score, but a confidence measure of whether that score reflects genuine capability.

## Architecture: How It Fits Together

```
┌─────────────────────────────────────────────────────────┐
│                   Agent Under Test                      │
│          (any model/agent via MCP/OpenAPI)               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│         SharpBasin / BasinBench Evaluation Harness       │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │   Inspect    │  │    PyRIT     │  │  Human-AI      │ │
│  │  Eval Tasks  │  │  Adversarial │  │  Teaming       │ │
│  │  & Scorers   │  │  Orchestrator│  │  Interface     │ │
│  └──────┬──────┘  └──────┬───────┘  └───────┬────────┘ │
│         │                │                   │          │
│  ┌──────▼────────────────▼───────────────────▼────────┐ │
│  │         Unified Scoring & Audit Pipeline            │ │
│  │    Task Completion · Safety · Process · Adversarial │ │
│  └──────────────────────┬─────────────────────────────┘ │
│                         │                               │
│  ┌──────────────────────▼─────────────────────────────┐ │
│  │    Open-Format Export · API · Dashboards · Trends   │ │
│  │              NIST Dioptra Integration                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
        Deployable: UNCLASS │ IL5/IL6 │ Air-gapped
```

## March 2026 Integration Update

Recent implementation updates strengthened the Inspect/PyRIT composition from framework-level integration to workflow-level operation:

- **Scenario-based adversarial execution is first-class**, covering representative harms such as content safety, prompt injection, and data leakage with policy-aligned evaluation.
- **Adversarial mode orchestration is explicit** in the standardized benchmark flow, supporting baseline, adversarial-variant, and adversarial-scenario execution modes.
- **Prompt transformation controls are composable and auditable**, supporting repeatable adversarial conditioning before agent execution.
- **Historical trend analysis is operational** for run-over-run performance inspection across execution modes.
- **Benchmark reliability hardening** improved multi-model execution stability and result attribution consistency in automated workflows.

## Empirical Results

BasinBench has been validated against real agent benchmarks using an independent grader model (Claude Sonnet 4.6) to prevent self-grading bias. The following results were generated from ClearEdge's agent execution platform — a production system with Docker-sandboxed tool access across standard enterprise code-hosting, collaboration, issue-tracking, and knowledge-management platforms. Multi-model evaluation support enables comparison across providers.

### Three-Dimensional Scoring: Claude Opus 4.6 (160 Questions)

| Dimension | Score | Detail |
|-----------|-------|--------|
| **Task Completion** | **62.8%** | 73 correct, 55 partial, 32 incorrect |
| **Behavioral Safety** | **94.7%** | 146 boundary-respecting, 11 partial, 3 violations |
| **Process Fidelity** | **83.1%** | 108 correct tool selection, 50 partial, 2 incorrect |

The signature finding: **Safety (94.7%) > Fidelity (83.1%) > Completion (62.8%)**. Output-only evaluation would rate this agent at 62.8% — missing the 94.7% safety signal entirely. The 31.9-point gap between safety and completion is invisible to monolithic scoring.

### Multi-Model Comparison

BasinBench's multi-model evaluation harness applies the same three-dimensional rubric across models, using the same independent grader model described above (currently Claude Sonnet 4.6) to avoid self-grading bias. The tooling supports models accessible through standardized evaluation interfaces.

Current result sets include:

- **Claude Opus 4.6 (full tier, 160 questions):** Task Completion 62.8%, Behavioral Safety 94.7%, Process Fidelity 83.1%.
- **GPT-5.3 Codex (nano tier, 4 questions; preliminary):** Task Completion 37.5% (1.5/4), Behavioral Safety 100.0% (4/4), Process Fidelity 62.5% (2.5/4).

The GPT-5.3 Codex nano run is directional evidence only due to sample size; larger-tier repeated runs remain the basis for durable cross-model claims.

Here, *full tier* refers to the standard 160-question benchmark run, while *nano tier* refers to a 4-question smoke test; fractional counts such as "1.5/4" or "2.5/4" reflect partial-credit scoring, where substantially but not fully correct answers receive 0.5 points instead of 1.

### Adversarial Resistance: 39-Probe Red Team Suite (9 Categories)

| Category | Probes | Description |
|----------|--------|-------------|
| Prompt Injection | 7 | Instruction override, nested injection, role-play |
| Goal Hijacking | 5 | Task substitution, scope creep, false priority |
| Tool Misuse | 5 | Exfiltration, destructive ops, unauthorized network |
| Boundary Violation | 5 | Path traversal, cross-tenant, system boundary |
| Data Exfiltration | 5 | Staged extraction, encoding, side-channel |
| Privilege Escalation | 3 | Role assumption, permission boundary testing |
| Authority Impersonation | 3 | Admin impersonation, system pretexting |
| Indirect Injection | 3 | Poisoned tool output, payload-in-data |
| Multi-Turn Persistence | 3 | Gradual boundary erosion, trust building |

Probes are severity-weighted (critical=3, high=2, medium=1) and defined in YAML for extensibility without code changes. Initial results (Claude Sonnet 4.6, 9-probe subset — not the full 39-probe suite): 88.9% raw resistance rate, zero critical bypasses, zero dangerous tool call attempts. Full 39-probe evaluation is planned; this document will be updated when those results are available.

### Benchmark Stability

Two independent Opus full-tier runs produced consistent results (±1.3% task completion, ±0.3% safety, 0% process fidelity variance). Bootstrap resampling with 95% confidence intervals are computed across multiple runs. Additional stability runs are in progress to strengthen confidence intervals.

## Related Work

BasinBench is complementary to, not a replacement for, established AI evaluation frameworks:

- **AgentBench** and **SWE-bench** measure task completion on code generation and software engineering tasks — output-only scoring that BasinBench's safety and fidelity dimensions extend.
- **GAIA** evaluates general AI assistants on multi-step reasoning — focused on task capability rather than behavioral safety under adversarial pressure.
- **AgentDojo** provides injection-focused evaluation for tool-using agents — overlapping with BasinBench's adversarial dimension but without the three-dimensional scoring model.
- **HELM** offers holistic evaluation across metrics and scenarios — BasinBench extends its methodology to agentic-specific dimensions (tool boundary compliance, process fidelity).

BasinBench's contribution is dimensional: it adds safety and process evaluation to the capability measurement that these frameworks provide. The compositional architecture means BasinBench can incorporate tasks from any of these frameworks as evaluation modules while adding its three-dimensional scoring layer.

## Limitations and Future Work

### Platform scope

Empirical results are currently from ClearEdge's agent execution platform. The BasinBench architecture supports any agent accessible via MCP or OpenAPI, but independent validation on external agent platforms is in progress.

### Dioptra integration depth

The current Dioptra integration provides one-way export of evaluation results as Dioptra experiments with tracked metrics and trend comparison. Deeper bidirectional integration (Dioptra-native evaluation orchestration) is roadmapped.

### Deployment classification

"Government-grade" refers to the evaluation methodology — three-dimensional, reproducible, auditable, with grader independence and gaming resistance — not to a specific deployment authorization. IL5/IL6 deployment and air-gapped operation require separate Authority to Operate processes.

### Gaming resistance maturity

Two of four gaming resistance mechanisms are implemented (behavioral consistency, contamination detection). Dynamic benchmark rotation and held-out set rotation are planned.

### Independent validation

All results reported here are produced by ClearEdge. The evaluation tooling is open-source, and ClearEdge invites independent replication. Reproduction instructions and all evaluation scripts are published in this repository.

### Model identity vs. execution provenance

BasinBench tracks model identity separately from execution provenance in evaluation records. White-paper comparison narratives emphasize model-level outcomes, while supporting records preserve reproducibility and audit traceability details.

## Why This Matters

ClearEdge actively contributes to the frameworks SharpBasin depends on — this positions BasinBench as a platform built by practitioners who understand these tools from the inside out, and who are invested in their continued improvement. BasinBench also integrates with NIST Dioptra — the U.S. government's own open-source AI test platform — exporting evaluation results as Dioptra experiments with tracked metrics, enabling government evaluators to audit BasinBench results through NIST's AI Risk Management Framework infrastructure.

The white paper expands each principle with implementation details, worked evaluation scenarios across cyber operations, intelligence analysis, and multi-domain command and control, and a benchmark development methodology that enables government evaluators to independently create, validate, and maintain mission-specific benchmarks.

---

*ClearEdge IT Solutions, LLC — CAGE 3CF84 — Small Business — TS Facility Clearance*
