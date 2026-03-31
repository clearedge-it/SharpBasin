# SharpBasin

**ClearEdge's AI Assessment Platform for Government-Grade Evaluation**

SharpBasin is ClearEdge IT Solutions' platform for testing, evaluating, and verifying AI systems — with a focus on agentic AI that invokes tools, accesses external data, and executes multi-step tasks autonomously.

## BasinBench

**BasinBench** is SharpBasin's evaluation and benchmarking suite. It composes two open-source evaluation frameworks and integrates with a third for audit and tracking:

| Framework | Origin | Role |
|---|---|---|
| [Inspect](https://github.com/UKGovernmentBEIS/inspect_ai) | UK AI Safety Institute | Structured evaluation workflows (Task → Solver → Scorer) |
| [PyRIT](https://github.com/Azure/PyRIT) | Microsoft | Adversarial red-teaming (prompt injection, goal hijacking, tool misuse) |
| [Dioptra](https://github.com/usnistgov/dioptra) | NIST | AI RMF-aligned trustworthiness tracking and audit export |

BasinBench evaluates agents across three dimensions simultaneously:

- **Task Completion** — did the agent achieve the objective?
- **Behavioral Safety** — did it respect defined boundaries?
- **Process Fidelity** — did it use appropriate tools and reasoning paths?

### Key Capabilities

- **Grader independence** — separate judge model prevents self-grading bias
- **39 adversarial probes** across 9 categories with severity-weighted scoring (YAML-driven, extensible without code changes)
- **Multi-model comparison** — cross-provider evaluation (Anthropic, OpenAI, open-weight)
- **Gaming resistance** — behavioral consistency checks and contamination detection
- **Statistical rigor** — bootstrap resampling with 95% confidence intervals
- **Dioptra integration** — export results as NIST AI RMF-aligned experiments

## Whitepaper

- [First Principles for Evaluating Agentic AI Systems](papers/first-principles-agentic-ai-evaluation.md) — Explains BasinBench's evaluation principles, architecture, and representative findings for agentic AI assessment.

## Framework Contributions

ClearEdge contributes upstream to the frameworks BasinBench depends on:

- **Inspect** — [Documentation improvements](https://github.com/UKGovernmentBEIS/inspect_ai/pull/3555)
- **PyRIT** — [Bug fix](https://github.com/Azure/PyRIT/pull/1526), approved by PyRIT maintainers

## Contact

ClearEdge IT Solutions, LLC — CAGE 3CF84 — Small Business — TS Facility Clearance

---

*SharpBasin and BasinBench are products of ClearEdge IT Solutions, LLC.*
