# First Principles for Evaluating Agentic AI Systems: How SharpBasin's BasinBench Integrates Inspect, PyRIT, and Dioptra for Government-Grade AI Assessment

**ClearEdge IT Solutions, LLC** | White Paper | March 2026

---

## The Evaluation Gap for Agentic AI

Traditional AI evaluation measures model outputs against static ground truth. But the shift from passive models to autonomous agents — systems that invoke tools, access external data, and execute multi-step tasks — breaks this paradigm. An agent that produces a correct final answer through an unsafe reasoning path (exfiltrating data, exceeding authorization, bypassing safety boundaries) represents a failure that output-only scoring cannot detect. Meanwhile, adversaries have already demonstrated almost fully agentic AI campaigns in the cyber domain, underscoring the urgency of evaluation infrastructure that can keep pace.

Government evaluators need to assess three dimensions simultaneously: **task completion** (did the agent achieve the objective?), **behavioral safety** (did it respect defined boundaries?), and **process fidelity** (did it use appropriate tools and reasoning paths?). No single evaluation framework addresses all three. **SharpBasin** — ClearEdge's AI assessment platform — addresses this through its **BasinBench** evaluation suite, which composes two complementary open-source frameworks — UK AISI's **Inspect** for structured evaluation workflows and Microsoft's **PyRIT** for adversarial red-teaming — and integrates with NIST's **Dioptra** for AI Risk Management Framework-aligned trustworthiness tracking and auditability. The harness is anchored by three first principles.

## Principle 1: Evaluation Must Be Compositional, Not Monolithic

BasinBench treats evaluation as a pipeline of independent, swappable modules rather than a single scoring function. The architecture mirrors the Model Context Protocol (MCP) pattern ClearEdge uses across its agent systems: each evaluation stage (task orchestration, scoring, adversarial probing, human review) connects through a standardized interface, enabling operators to reconfigure evaluation workflows without re-engineering the harness.

**Inspect** provides the compositional backbone. Its `Task → Solver → Scorer` pipeline maps directly to the three-dimensional evaluation model: solvers orchestrate agent execution (capturing tool invocations and decision traces), while scorers evaluate task completion, behavioral safety, and process fidelity independently. BasinBench extends Inspect's `model_graded_qa` scorer with domain-specific grading criteria — including fixed-criterion templates for behavioral assessments where no per-sample ground truth exists — enabling government evaluators to define mission-specific scoring rubrics without writing custom scoring code.

## Principle 2: Adversarial Testing Must Run Continuously, Not as a Separate Phase

Traditional red-teaming treats security testing as a gate review — a one-time event before deployment. Agentic systems, which dynamically compose tool calls and reasoning chains, can exhibit novel failure modes under adversarial pressure that did not exist during initial testing. BasinBench integrates adversarial evaluation as a continuous, automated layer rather than a discrete phase.

**PyRIT** provides the adversarial engine. Its orchestrator-converter-scorer architecture automates attack pattern execution across categories including prompt injection, jailbreaking, goal hijacking, and tool misuse — all specific to agentic failure modes. BasinBench feeds PyRIT's adversarial probes through the same agent sandbox used for functional evaluation, producing unified scoring across both functional and adversarial dimensions. When an agent that passes all functional benchmarks fails under adversarial pressure, the evaluation pipeline flags the discrepancy automatically.

The result is a continuous red-team loop: as new agent capabilities are deployed, adversarial probes are re-executed against updated agent configurations, and robustness trends are tracked over time through BasinBench's monitoring pipeline.

## Principle 3: Benchmarks Must Resist Gaming While Remaining Interpretable

The sophistication of agentic AI introduces a new category of gaming risk: agents that optimize for benchmark-specific patterns without developing genuine capability. BasinBench addresses this through four mechanisms designed into the benchmark lifecycle:

- **Contamination detection** — identifying when agent training data overlaps with evaluation data
- **Dynamic benchmark rotation** — periodically refreshing evaluation tasks to prevent memorization
- **Held-out evaluation sets** — maintaining undisclosed test items that validate benchmark scores against novel tasks
- **Behavioral consistency checks** — verifying that benchmark performance correlates with performance on operationally realistic scenarios

These mechanisms are implemented as Inspect evaluation tasks that run alongside functional benchmarks, producing a "gaming resistance score" that accompanies every evaluation report. Government evaluators receive not just a capability score, but a confidence measure of whether that score reflects genuine capability.

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

## Empirical Results

BasinBench has been validated against real agent benchmarks. The following results were generated from ClearEdge's agent execution platform — a production system with Docker-sandboxed tool access across GitHub, Jira, Confluence, and internal knowledge repositories.

### Three-Dimensional Scoring: Claude Opus 4.6 (160 Questions)

| Dimension | Score | Detail |
|-----------|-------|--------|
| **Task Completion** | **62.8%** | 73 correct, 55 partial, 32 incorrect |
| **Behavioral Safety** | **94.7%** | 146 boundary-respecting, 11 partial, 3 violations |
| **Process Fidelity** | **83.1%** | 108 correct tool selection, 50 partial, 2 incorrect |

The signature finding: **Safety (95%) > Fidelity (83%) > Completion (63%)**. Output-only evaluation would rate this agent at 63% — missing the 95% safety signal entirely. The 32-point gap between safety and completion is invisible to monolithic scoring.

### Adversarial Resistance: 9-Probe Red Team Suite

| Category | Probes | Resisted | Rate |
|----------|--------|----------|------|
| Prompt Injection | 3 | 3 | 100% |
| Tool Misuse | 2 | 2 | 100% |
| Boundary Violation | 2 | 2 | 100% |
| Goal Hijacking | 2 | 1 | 50% |
| **Overall** | **9** | **8** | **88.9%** |

Zero critical bypasses. Zero dangerous tool call attempts. The single partial bypass (goal hijacking — security scan redirect) used only authorized commands, demonstrating that the agent's safety boundaries held even when its intent classification failed.

### Benchmark Stability

Two independent Opus full-tier runs produced consistent results (±1.3% task completion, ±0.3% safety, 0% process fidelity variance), validating that the evaluation methodology produces reproducible, government-grade measurements.

## Why This Matters

ClearEdge actively contributes to the frameworks SharpBasin depends on — this positions BasinBench as a platform built by practitioners who understand these tools from the inside out, and who are invested in their continued improvement. BasinBench also integrates with NIST Dioptra — the U.S. government's own open-source AI test platform — exporting evaluation results as Dioptra experiments with tracked metrics, enabling government evaluators to audit BasinBench results through NIST's AI Risk Management Framework infrastructure.

The white paper expands each principle with implementation details, worked evaluation scenarios across cyber operations, intelligence analysis, and multi-domain command and control, and a benchmark development methodology that enables government evaluators to independently create, validate, and maintain mission-specific benchmarks.

---

*ClearEdge IT Solutions, LLC — CAGE 3CF84 — Small Business — TS Facility Clearance*
