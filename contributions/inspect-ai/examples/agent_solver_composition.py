"""Agent Solver Composition Cookbook

This example demonstrates how to compose multiple solver variants for agent
evaluation without duplicating the core agent loop. Three solvers share a
single ``_run_agent_loop`` helper:

1. ``mcp_agent_solver``        — baseline: direct tool use
2. ``mcp_agent_solver_cot``    — chain-of-thought elicitation before tool use
3. ``mcp_agent_solver_critique`` — self-critique after initial response

The pattern is useful when you want to compare elicitation strategies on the
same underlying agent capability without changing the tool interface or the
scoring logic.

Contribution target: ``docs/`` or ``examples/`` in
https://github.com/UKGovernmentBEIS/inspect_ai

Usage
-----
Run the baseline solver::

    inspect eval agent_solver_composition.py -T solver=baseline

Run the chain-of-thought variant::

    inspect eval agent_solver_composition.py -T solver=cot

Run the self-critique variant::

    inspect eval agent_solver_composition.py -T solver=critique

Compare all three on the same dataset::

    for variant in baseline cot critique; do
        inspect eval agent_solver_composition.py -T solver=$variant \\
            --log-dir ./logs/$variant
    done
"""

from __future__ import annotations

from typing import Sequence

from inspect_ai import Task, task
from inspect_ai.dataset import Sample, MemoryDataset
from inspect_ai.model import (
    ChatMessage,
    ChatMessageSystem,
    ChatMessageUser,
    get_model,
)
from inspect_ai.scorer import Score, Scorer, mean, scorer, stderr
from inspect_ai.solver import Generate, Solver, TaskState, solver
from inspect_ai.tool import Tool, bash, web_search


# ---------------------------------------------------------------------------
# Shared agent loop
# ---------------------------------------------------------------------------

async def _run_agent_loop(
    state: TaskState,
    tools: Sequence[Tool],
    system_prompt: str,
    max_iterations: int = 10,
) -> TaskState:
    """Run a tool-use loop until the model stops calling tools.

    This helper is shared by all solver variants so that the core agent
    behaviour is defined in exactly one place. Variants differ only in
    how they prepare ``state.messages`` before calling this function.

    Args:
        state: Current task state (messages + output).
        tools: Tools available to the agent.
        max_iterations: Safety limit on the number of generate-execute cycles.

    Returns:
        Updated task state after the agent loop completes.
    """
    model = get_model()

    # Prepend system prompt if not already present
    if not any(isinstance(m, ChatMessageSystem) for m in state.messages):
        state.messages.insert(0, ChatMessageSystem(content=system_prompt))

    for _ in range(max_iterations):
        # Generate a response (may include tool calls)
        output = await model.generate(input=state.messages, tools=tools)
        state.messages.append(output.message)
        state.output = output

        # If the model made no tool calls, the loop is complete
        if not output.message.tool_calls:
            break

        # Execute tool calls and append results
        from inspect_ai.model import execute_tools  # local import for clarity
        tool_results = await execute_tools(output.message, tools)
        state.messages.extend(tool_results)

    return state


# ---------------------------------------------------------------------------
# Solver 1: Baseline — direct tool use
# ---------------------------------------------------------------------------

BASELINE_SYSTEM = """\
You are a capable assistant with access to tools. Use them to complete the
task as efficiently as possible. When you have finished, provide a clear
summary of what you did and the result.
"""


@solver
def mcp_agent_solver(
    tools: Sequence[Tool] | None = None,
    max_iterations: int = 10,
) -> Solver:
    """Baseline agent solver: direct tool use without elicitation scaffolding.

    The model receives the task and immediately begins using tools. This is
    the control condition for comparing elicitation strategies.

    Args:
        tools: Tools to make available. Defaults to ``[bash(), web_search()]``.
        max_iterations: Maximum tool-use iterations before terminating.
    """
    _tools = list(tools) if tools is not None else [bash(), web_search()]

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        return await _run_agent_loop(
            state=state,
            tools=_tools,
            system_prompt=BASELINE_SYSTEM,
            max_iterations=max_iterations,
        )

    return solve


# ---------------------------------------------------------------------------
# Solver 2: Chain-of-thought — elicit reasoning before tool use
# ---------------------------------------------------------------------------

COT_SYSTEM = """\
You are a capable assistant with access to tools. Before using any tools,
think step-by-step about the task:

1. What is the goal?
2. What information do I already have?
3. What tools do I need and in what order?
4. What could go wrong and how will I handle it?

After your reasoning, proceed to use the tools and complete the task.
"""

COT_ELICITATION = """\
Before you begin, please think step-by-step about how you will approach this
task. Consider what tools you will need and in what order you will use them.
"""


@solver
def mcp_agent_solver_cot(
    tools: Sequence[Tool] | None = None,
    max_iterations: int = 10,
) -> Solver:
    """Chain-of-thought agent solver: elicit reasoning before tool use.

    Inserts a chain-of-thought elicitation turn before the agent loop begins.
    The model's reasoning is preserved in the conversation history and
    influences subsequent tool-use decisions.

    This variant is useful for measuring whether explicit reasoning elicitation
    improves task completion or process fidelity without changing the tool
    interface.

    Args:
        tools: Tools to make available. Defaults to ``[bash(), web_search()]``.
        max_iterations: Maximum tool-use iterations before terminating.
    """
    _tools = list(tools) if tools is not None else [bash(), web_search()]

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        # Inject chain-of-thought elicitation as a user turn
        state.messages.append(ChatMessageUser(content=COT_ELICITATION))

        # Get the model's reasoning (no tools yet — pure text generation)
        model = get_model()
        reasoning_output = await model.generate(
            input=state.messages,
            tools=[],  # no tools during reasoning phase
        )
        state.messages.append(reasoning_output.message)

        # Now run the full agent loop with tools
        return await _run_agent_loop(
            state=state,
            tools=_tools,
            system_prompt=COT_SYSTEM,
            max_iterations=max_iterations,
        )

    return solve


# ---------------------------------------------------------------------------
# Solver 3: Self-critique — review and revise after initial response
# ---------------------------------------------------------------------------

CRITIQUE_SYSTEM = """\
You are a careful assistant with access to tools. Complete the task, then
critically review your own work before finalising your answer.
"""

CRITIQUE_PROMPT = """\
Please review your response above. Consider:

1. Did you fully address the task objective?
2. Are there any errors or omissions in your work?
3. Did you use the most appropriate tools?

If you identify any issues, correct them now. If your response is complete
and correct, confirm this and provide your final answer.
"""


@solver
def mcp_agent_solver_critique(
    tools: Sequence[Tool] | None = None,
    max_iterations: int = 10,
    critique_model: str | None = None,
) -> Solver:
    """Self-critique agent solver: review and revise after initial response.

    Runs the agent loop to produce an initial response, then injects a
    self-critique prompt and runs a second (shorter) loop to allow the model
    to correct any errors it identifies.

    This variant is useful for measuring whether self-review improves output
    quality without changing the tool interface or the scoring rubric.

    Args:
        tools: Tools to make available. Defaults to ``[bash(), web_search()]``.
        max_iterations: Maximum tool-use iterations per phase (initial +
            critique phases each get this many iterations).
        critique_model: Model to use for the critique phase. Defaults to the
            same model as the evaluation (``get_model()``).
    """
    _tools = list(tools) if tools is not None else [bash(), web_search()]

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        # Phase 1: initial agent loop
        state = await _run_agent_loop(
            state=state,
            tools=_tools,
            system_prompt=CRITIQUE_SYSTEM,
            max_iterations=max_iterations,
        )

        # Phase 2: self-critique
        state.messages.append(ChatMessageUser(content=CRITIQUE_PROMPT))

        critique_gen = get_model(critique_model) if critique_model else get_model()
        critique_output = await critique_gen.generate(
            input=state.messages,
            tools=_tools,
        )
        state.messages.append(critique_output.message)
        state.output = critique_output

        # If the critique triggered more tool calls, run a short follow-up loop
        if critique_output.message.tool_calls:
            state = await _run_agent_loop(
                state=state,
                tools=_tools,
                system_prompt=CRITIQUE_SYSTEM,
                max_iterations=max_iterations // 2 or 1,
            )

        return state

    return solve


# ---------------------------------------------------------------------------
# Scorer: simple model-graded task completion
# ---------------------------------------------------------------------------

_GRADER_PROMPT = """\
Did the agent successfully complete the following task?

Task: {task}
Agent response: {response}

Respond with a score from 0.0 (complete failure) to 1.0 (full success).
Respond with only the numeric score.
"""


@scorer(metrics=[mean(), stderr()])
def task_completion_scorer(grader_model: str = "openai/gpt-4o") -> Scorer:
    """Grade task completion on a 0–1 continuous scale."""
    async def score(state: TaskState, target) -> Score:
        model = get_model(grader_model)
        result = await model.generate([
            ChatMessageUser(content=_GRADER_PROMPT.format(
                task=state.input_text,
                response=state.output.completion,
            ))
        ])
        try:
            value = float(result.completion.strip())
        except ValueError:
            value = 0.0
        return Score(value=value)

    return score


# ---------------------------------------------------------------------------
# Task definition
# ---------------------------------------------------------------------------

_SAMPLE_TASKS = [
    Sample(
        id="file-list",
        input="List all Python files in the current directory and count them.",
        target="A count of Python files with their names.",
    ),
    Sample(
        id="web-lookup",
        input="Find the current version of the Inspect AI framework.",
        target="The current Inspect AI version number.",
    ),
    Sample(
        id="multi-step",
        input=(
            "Create a file called 'hello.txt' containing the text 'Hello, Inspect!', "
            "then read it back and confirm the contents."
        ),
        target="Confirmation that hello.txt contains 'Hello, Inspect!'.",
    ),
]


@task
def agent_composition_demo(solver: str = "baseline") -> Task:
    """Demonstrate solver composition for agent evaluation.

    Args:
        solver: Which solver variant to use. One of ``baseline``, ``cot``,
            or ``critique``.
    """
    solver_map = {
        "baseline": mcp_agent_solver(),
        "cot":      mcp_agent_solver_cot(),
        "critique": mcp_agent_solver_critique(),
    }
    if solver not in solver_map:
        raise ValueError(f"Unknown solver '{solver}'. Choose from: {list(solver_map)}")

    return Task(
        dataset=MemoryDataset(_SAMPLE_TASKS),
        solver=solver_map[solver],
        scorer=task_completion_scorer(),
    )
