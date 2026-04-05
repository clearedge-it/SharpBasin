# Agent Solver Composition Cookbook

This example shows how to compose multiple solver variants for agent evaluation
from a **single shared `_run_agent_loop` helper**, reducing duplication while
enabling controlled comparisons between prompting strategies.

## Solvers

| Solver | Description |
|--------|-------------|
| `mcp_agent_solver` | Baseline — tool-calling agent with no extra prompting |
| `mcp_agent_solver_cot` | Chain-of-thought — elicits step-by-step reasoning before acting |
| `mcp_agent_solver_critique` | Self-critique — agent reviews its own plan before executing |

All three solvers share the same `_run_agent_loop` implementation so that
differences in evaluation results are attributable to the prompting strategy,
not to incidental implementation differences.

## Running the Examples

```bash
# Baseline
inspect eval agent_solver_composition.py@agent_eval_baseline

# Chain-of-thought
inspect eval agent_solver_composition.py@agent_eval_cot

# Self-critique
inspect eval agent_solver_composition.py@agent_eval_critique

# Compare all three in the viewer
inspect view
```

## Key Design Patterns

### Shared Agent Loop

The `_run_agent_loop` helper encapsulates the tool-calling loop:

```python
async def _run_agent_loop(state, generate, tools, *, max_iterations=10):
    for _ in range(max_iterations):
        state = await generate(state, tools=tools)
        if not state.output.message.tool_calls:
            break
    return state
```

Each solver variant calls this helper after applying its own prompting
strategy. This means:

- Bug fixes to the loop apply to all variants simultaneously
- The tool interface is identical across variants (no confounds)
- Adding a new variant requires only a new `@solver` function

### Eliciting Reasoning Without Changing the Tool Interface

The CoT and self-critique variants inject prompts into the message history
**before** the agent loop starts. The tools available to the model are
identical in all three variants — only the system prompt differs.

This is important for fair comparison: if you changed the tools between
variants, you would not know whether performance differences were due to
the prompting strategy or the tool availability.

### Optional Separate Critique Model

The `mcp_agent_solver_critique` solver accepts an optional `critique_model`
parameter. When provided, a stronger model performs the critique step while
the weaker model under evaluation handles tool calls:

```python
solver = mcp_agent_solver_critique(critique_model="openai/gpt-4o")
```

This lets you measure whether external critique improves a weaker model's
tool-use accuracy.

## Requirements

- Docker (for the `sandbox="docker"` configuration)
- `inspect-ai` installed: `pip install inspect-ai`
