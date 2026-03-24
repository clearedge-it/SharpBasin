# SharpBasin

**ClearEdge's AI Assessment Platform for Government-Grade Evaluation**

SharpBasin is ClearEdge IT Solutions' platform for testing, evaluating, and verifying AI systems — with a focus on agentic AI that invokes tools, accesses external data, and executes multi-step tasks autonomously.

## BasinBench

**BasinBench** is SharpBasin's evaluation and benchmarking suite. It composes three open-source frameworks into a unified harness:

| Framework | Origin | Role |
|---|---|---|
| [Inspect](https://github.com/UKGovernmentBEIS/inspect_ai) | UK AI Safety Institute | Structured evaluation workflows (Task → Solver → Scorer) |
| [PyRIT](https://github.com/Azure/PyRIT) | Microsoft | Adversarial red-teaming (prompt injection, goal hijacking, tool misuse) |
| [Dioptra](https://github.com/usnistgov/dioptra) | NIST | AI Risk Management Framework-aligned trustworthiness tracking |

BasinBench evaluates agents across three dimensions simultaneously:

- **Task Completion** — did the agent achieve the objective?
- **Behavioral Safety** — did it respect defined boundaries?
- **Process Fidelity** — did it use appropriate tools and reasoning paths?

## Published Research

- [First Principles for Evaluating Agentic AI Systems](papers/first-principles-agentic-ai-evaluation.md) — How BasinBench integrates Inspect, PyRIT, and Dioptra for government-grade AI assessment (March 2026)

## Framework Contributions

ClearEdge contributes upstream to the frameworks BasinBench depends on:

- **Inspect** — [Documentation improvements](https://github.com/UKGovernmentBEIS/inspect_ai/pull/3555)
- **PyRIT** — [Bug fix](https://github.com/Azure/PyRIT/pull/1526), approved by PyRIT maintainers

## Contact

ClearEdge IT Solutions, LLC — CAGE 3CF84 — Small Business — TS Facility Clearance

---

*SharpBasin and BasinBench are products of ClearEdge IT Solutions, LLC.*
