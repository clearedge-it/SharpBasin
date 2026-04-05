"""
Agent Solver Composition Cookbook
==================================

This example demonstrates how to compose multiple solver variants for agent
evaluation from a single shared ``_run_agent_loop`` helper.  Three solvers
are provided:

* ``mcp_agent_solver``         — baseline: tool-calling agent with no extra prompting
* ``mcp_agent_solver_cot``     — chain-of-thought variant: elicits step-by-step reasoning
* ``mcp_agent_solver_critique``— self-critique variant: agent reviews its own plan before acting

All three share the same ``_run_agent_loop`` implementation so that differences
in evaluation results are attributable to the prompting strategy, not to
incidental implementation differences.

Usage
-----
Run the baseline solver::

    inspect eval agent_solver_composition.py@agent_eval_baseline

Run the chain-of-thought variant::

    inspect eval agent_solver_composition.py@agent_eval_cot

Run the self-critique variant::

    inspect eval agent_solver_composition.py@agent_eval_critique

Compare all three in the Inspect viewer::

    inspect view
"""

from __future__ import annotations

from textwrap import dedent
from typing import Sequence

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, json_dataset
from inspect_ai.model import ChatMessageUser, get_model
from inspect_ai.scorer import includes
from inspect_ai.solver import Generate, Solver, TaskState, generate, solver, system_message
from inspect_ai.tool import Tool, bash, python


# ---------------------------------------------------------------------------
# Shared agent loop
# ---------------------------------------------------------------------------

async def _run_agent_loop(
    state: TaskState,
    generate: Generate,
    tools: Sequence[Tool],
    *,
    max_iterations: int = 10,
) -> TaskState:
    """
    Core agent loop shared by all solver variants.

    Runs a tool-calling loop until the model stops requesting tool calls or
    ``max_iterations`` is reached.  Each iteration:

    1. Calls the model with the current message history.
    2. If the model returned tool calls, executes them and appends results.
    3. If the model returned no tool calls, the loop exits.

    Args:
        state:          Current task state (messages + output).
        generate:       The ``Generate`` callable provided by Inspect.
        tools:          Tools available to the agent.
        max_iterations: Safety limit on the number of model calls.

    Returns:
        Updated ``TaskState`` after the agent loop completes.
    """
    for _ in range(max_iterations):
        state = await generate(state, tools=tools)

        # Exit when the model stops making tool calls
        if not state.output.message.tool_calls:
            break

    return state


# ---------------------------------------------------------------------------
# Baseline solver
# ---------------------------------------------------------------------------

@solver
def mcp_agent_solver(
    tools: Sequence[Tool] | None = None,
    max_iterations: int = 10,
) -> Solver:
    """
    Baseline agent solver.

    Provides the model with a set of tools and runs the shared agent loop
    with no additional prompting.  Use this as the control condition when
    comparing prompting strategies.

    Args:
        tools:          Tools to make available.  Defaults to bash + python.
        max_iterations: Maximum number of model calls per sample.
    """
    _tools = list(tools) if tools is not None else [bash(), python()]

    async def solve(state: TaskState, gen: Generate) -> TaskState:
        return await _run_agent_loop(state, gen, _tools, max_iterations=max_iterations)

    return solve


# ---------------------------------------------------------------------------
# Chain-of-thought variant
# ---------------------------------------------------------------------------

_COT_SYSTEM_PROMPT = dedent("""\
    Before taking any action, think step by step:

    1. Restate the goal in your own words.
    2. List the tools available to you.
    3. Outline a plan — what will you do first, second, and so on?
    4. Execute the plan one step at a time, explaining each action.

    Do not skip the planning step even for simple tasks.
""")


@solver
def mcp_agent_solver_cot(
    tools: Sequence[Tool] | None = None,
    max_iterations: int = 10,
) -> Solver:
    """
    Chain-of-thought agent solver.

    Prepends a system prompt that instructs the model to reason step-by-step
    before acting.  The tool interface is identical to ``mcp_agent_solver``
    so that differences in results are attributable to the CoT elicitation.

    Args:
        tools:          Tools to make available.  Defaults to bash + python.
        max_iterations: Maximum number of model calls per sample.
    """
    _tools = list(tools) if tools is not None else [bash(), python()]

    async def solve(state: TaskState, gen: Generate) -> TaskState:
        # Inject the CoT system prompt before running the shared loop
        cot_solver = system_message(_COT_SYSTEM_PROMPT)
        state = await cot_solver(state, gen)
        return await _run_agent_loop(state, gen, _tools, max_iterations=max_iterations)

    return solve


# ---------------------------------------------------------------------------
# Self-critique variant
# ---------------------------------------------------------------------------

_CRITIQUE_PROMPT = dedent("""\
    Review the plan you just described.  Ask yourself:

    * Is each step necessary?
    * Could any step cause unintended side-effects?
    * Is there a simpler approach?

    Revise your plan if needed, then proceed with the revised version.
""")


@solver
def mcp_agent_solver_critique(
    tools: Sequence[Tool] | None = None,
    max_iterations: int = 10,
    critique_model: str | None = None,
) -> Solver:
    """
    Self-critique agent solver.

    After the model produces its initial plan (first generation), injects a
    critique prompt and asks the model to revise before acting.  The critique
    can optionally be performed by a separate model (e.g. a stronger grader
    model) while the tool-calling is done by the evaluated model.

    Args:
        tools:           Tools to make available.  Defaults to bash + python.
        max_iterations:  Maximum number of model calls per sample.
        critique_model:  Optional model name for the critique step.  If None,
                         the model under evaluation performs self-critique.
    """
    _tools = list(tools) if tools is not None else [bash(), python()]

    async def solve(state: TaskState, gen: Generate) -> TaskState:
        # Step 1: Ask the model to produce an initial plan (no tools yet)
        state = await gen(state)

        # Step 2: Inject the critique prompt
        state.messages.append(ChatMessageUser(content=_CRITIQUE_PROMPT))

        # Step 3: Optionally use a separate model for the critique response
        if critique_model is not None:
            critic = get_model(critique_model)
            critique_output = await critic.generate(state.messages)
            from inspect_ai.model import ChatMessageAssistant
            state.messages.append(
                ChatMessageAssistant(content=critique_output.completion)
            )
        else:
            # Self-critique: the evaluated model responds to its own plan
            state = await gen(state)

        # Step 4: Run the shared agent loop with tools now available
        return await _run_agent_loop(state, gen, _tools, max_iterations=max_iterations)

    return solve


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def _sample_dataset() -> list[Sample]:
    """Minimal inline dataset for demonstration purposes."""
    return [
        Sample(
            input="List all Python files in the current directory and count them.",
            target=["python files", ".py"],
        ),
        Sample(
            input="Create a file named 'hello.txt' containing the text 'Hello, world!'.",
            target=["hello.txt", "Hello, world!"],
        ),
        Sample(
            input="What is the current working directory?",
            target=["/"],
        ),
    ]


@task
def agent_eval_baseline() -> Task:
    """Baseline agent evaluation — no extra prompting."""
    return Task(
        dataset=_sample_dataset(),
        solver=mcp_agent_solver(),
        scorer=includes(),
        sandbox="docker",
    )


@task
def agent_eval_cot() -> Task:
    """Chain-of-thought agent evaluation."""
    return Task(
        dataset=_sample_dataset(),
        solver=mcp_agent_solver_cot(),
        scorer=includes(),
        sandbox="docker",
    )


@task
def agent_eval_critique() -> Task:
    """Self-critique agent evaluation."""
    return Task(
        dataset=_sample_dataset(),
        solver=mcp_agent_solver_critique(),
        scorer=includes(),
        sandbox="docker",
    )
